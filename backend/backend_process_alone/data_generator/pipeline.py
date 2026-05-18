"""
Pipeline — End-to-end orchestrator for e-invoice transcoding.

Takes an invoice row (or entire CSV) and produces mapping predictions:
  target_format, is_mapping_valid, mapping_errors, corrected_fields
"""

import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FORMAT_BY_NAME, COUNTRY_FORMAT_MAP
from format_resolver import (
    resolve_target_format, get_format_rules, get_source_format_rules,
    load_format_rules_from_csv, build_country_format_map,
)
from transcoder import Transcoder
from validator import Validator


# ═══════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════

class InvoicePipeline:
    """
    End-to-end invoice transcoding and validation pipeline.

    Flow:
      1. Resolve target format from target_country
      2. Transcode fields (source format → target format)
      3. Validate transcoded invoice (7 error checks)
      4. Output mapping result
    """

    def __init__(self, format_rules_path: str = None):
        """
        Initialize the pipeline.

        Args:
            format_rules_path: Path to format_rules.csv.
                             If None, uses hardcoded config.
        """
        if format_rules_path and os.path.exists(format_rules_path):
            self.format_rules = load_format_rules_from_csv(format_rules_path)
            self.country_map = build_country_format_map(self.format_rules)
            print(f"  📋 Loaded {len(self.format_rules)} format rules from {format_rules_path}")
            print(f"  🌍 Country mappings: {self.country_map}")
        else:
            self.format_rules = FORMAT_BY_NAME
            self.country_map = COUNTRY_FORMAT_MAP
            print("  📋 Using hardcoded format rules from config.py")

    def process_invoice(self, invoice: dict) -> dict:
        """
        Process a single invoice row through the full pipeline.

        Args:
            invoice: Dict with fields from invoices_source/test.csv

        Returns:
            Dict with: invoice_id, target_format, is_mapping_valid,
                       mapping_errors, corrected_fields
        """
        invoice_id = invoice.get("invoice_id", "UNKNOWN")
        source_format = invoice.get("source_format", "")
        target_country = invoice.get("target_country", "")

        # Step 1: Resolve target format
        target_format = resolve_target_format(target_country, self.country_map)
        if not target_format:
            return {
                "invoice_id": invoice_id,
                "target_format": "unknown",
                "is_mapping_valid": False,
                "mapping_errors": "missing_required_field",
                "corrected_fields": json.dumps({"target_country": "unsupported"}),
            }

        # Step 2: Get format rules
        source_rules = self.format_rules.get(source_format)
        target_rules = self.format_rules.get(target_format)

        if not source_rules:
            return {
                "invoice_id": invoice_id,
                "target_format": target_format,
                "is_mapping_valid": False,
                "mapping_errors": "missing_required_field",
                "corrected_fields": json.dumps({"source_format": "unknown"}),
            }

        if not target_rules:
            return {
                "invoice_id": invoice_id,
                "target_format": target_format,
                "is_mapping_valid": False,
                "mapping_errors": "missing_required_field",
                "corrected_fields": json.dumps({"target_format": "unknown"}),
            }

        # Step 3: Transcode
        transcoder = Transcoder(source_rules, target_rules)
        transcoded = transcoder.transcode(invoice)

        # Step 4: Validate (use ORIGINAL invoice to detect structure issues,
        # but transcoded for field mapping validation)
        validator = Validator(source_rules, target_rules)
        is_valid, errors, corrections = validator.validate(invoice)

        # Step 5: Build output
        return {
            "invoice_id": invoice_id,
            "target_format": target_format,
            "is_mapping_valid": is_valid,
            "mapping_errors": "|".join(errors) if errors else "",
            "corrected_fields": json.dumps(corrections) if corrections else "{}",
        }

    def process_csv(self, input_csv: str, output_csv: str) -> list:
        """
        Process an entire invoice CSV and write mapping predictions.

        Args:
            input_csv: Path to invoices CSV (source or test)
            output_csv: Path to write predictions CSV

        Returns:
            List of prediction dicts
        """
        predictions = []

        # Read invoices
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            invoices = list(reader)

        print(f"\n  🔄 Processing {len(invoices)} invoices...")

        # Process each invoice
        for i, invoice in enumerate(invoices):
            result = self.process_invoice(invoice)
            predictions.append(result)

            if (i + 1) % 500 == 0:
                print(f"    Processed {i + 1}/{len(invoices)}...")

        # Write output
        output_dir = os.path.dirname(output_csv)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        fieldnames = [
            "invoice_id", "target_format", "is_mapping_valid",
            "mapping_errors", "corrected_fields",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(predictions)

        print(f"  ✅ Predictions written to {output_csv}")
        return predictions


# ═══════════════════════════════════════════════════════════
# EVALUATION
# ═══════════════════════════════════════════════════════════

def evaluate_predictions(predictions: list, ground_truth_path: str) -> dict:
    """
    Compare pipeline predictions against ground truth mappings.

    Returns:
        Dict with accuracy metrics
    """
    # Load ground truth
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        truth = {row["invoice_id"]: row for row in reader}

    total = len(predictions)
    correct_format = 0
    correct_validity = 0
    correct_errors = 0
    correct_full = 0

    # Per-error-type metrics
    error_tp = Counter()  # True positives
    error_fp = Counter()  # False positives
    error_fn = Counter()  # False negatives

    for pred in predictions:
        inv_id = pred["invoice_id"]
        true = truth.get(inv_id)
        if not true:
            continue

        # Check target format
        fmt_match = pred["target_format"] == true["target_format"]
        if fmt_match:
            correct_format += 1

        # Check is_mapping_valid
        pred_valid = str(pred["is_mapping_valid"])
        true_valid = str(true["is_mapping_valid"])
        validity_match = pred_valid == true_valid
        if validity_match:
            correct_validity += 1

        # Check error types
        pred_errors = set(pred["mapping_errors"].split("|")) if pred["mapping_errors"] else set()
        true_errors = set(true["mapping_errors"].split("|")) if true["mapping_errors"] else set()

        if pred_errors == true_errors:
            correct_errors += 1

        # Per-error metrics
        for err in pred_errors | true_errors:
            if err in pred_errors and err in true_errors:
                error_tp[err] += 1
            elif err in pred_errors and err not in true_errors:
                error_fp[err] += 1
            elif err not in pred_errors and err in true_errors:
                error_fn[err] += 1

        # Full match
        if fmt_match and validity_match and pred_errors == true_errors:
            correct_full += 1

    # Calculate metrics
    metrics = {
        "total": total,
        "format_accuracy": correct_format / total if total else 0,
        "validity_accuracy": correct_validity / total if total else 0,
        "error_type_accuracy": correct_errors / total if total else 0,
        "full_accuracy": correct_full / total if total else 0,
    }

    # Per-error precision/recall
    all_error_types = set(error_tp.keys()) | set(error_fp.keys()) | set(error_fn.keys())
    error_metrics = {}
    for err in sorted(all_error_types):
        tp = error_tp[err]
        fp = error_fp[err]
        fn = error_fn[err]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        error_metrics[err] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
    metrics["per_error_metrics"] = error_metrics

    return metrics


def print_evaluation(metrics: dict):
    """Pretty-print evaluation metrics."""
    print(f"\n{'='*60}")
    print(f"  📊 Pipeline Evaluation Results")
    print(f"{'='*60}")
    print(f"  Total invoices evaluated: {metrics['total']}")
    print(f"  Target format accuracy:   {metrics['format_accuracy']:.1%}")
    print(f"  Validity accuracy:        {metrics['validity_accuracy']:.1%}")
    print(f"  Error type accuracy:       {metrics['error_type_accuracy']:.1%}")
    print(f"  Full match accuracy:       {metrics['full_accuracy']:.1%}")

    per_error = metrics.get("per_error_metrics", {})
    if per_error:
        print(f"\n  Per-Error-Type Metrics:")
        print(f"  {'Error Type':<40} {'Prec':>6} {'Rec':>6} {'F1':>6} {'TP':>5} {'FP':>5} {'FN':>5}")
        print(f"  {'-'*80}")
        for err, m in sorted(per_error.items()):
            print(f"  {err:<40} {m['precision']:>6.2%} {m['recall']:>6.2%} {m['f1']:>6.2%} {m['tp']:>5} {m['fp']:>5} {m['fn']:>5}")


# ═══════════════════════════════════════════════════════════
# MAIN — Run pipeline on training data for validation
# ═══════════════════════════════════════════════════════════

def main():
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

    print("\n🚀 E-Invoice Transcoding Pipeline")
    print("=" * 60)

    # Initialize pipeline with format_rules.csv
    format_rules_path = os.path.join(DATA_DIR, "format_rules.csv")
    pipeline = InvoicePipeline(format_rules_path)

    # Process training data
    print("\n📁 Phase 1: Validating against training data...")
    source_csv = os.path.join(DATA_DIR, "invoices_source.csv")
    train_output = os.path.join(DATA_DIR, "predictions_train.csv")
    train_preds = pipeline.process_csv(source_csv, train_output)

    # Evaluate against training ground truth
    train_truth = os.path.join(DATA_DIR, "mappings_train.csv")
    if os.path.exists(train_truth):
        metrics = evaluate_predictions(train_preds, train_truth)
        print_evaluation(metrics)

    # Process test data
    print("\n📁 Phase 2: Processing test data...")
    test_csv = os.path.join(DATA_DIR, "invoices_test.csv")
    test_output = os.path.join(DATA_DIR, "predictions_output.csv")
    test_preds = pipeline.process_csv(test_csv, test_output)

    # Evaluate against test ground truth (our own, for validation)
    test_truth = os.path.join(DATA_DIR, "mappings_test_ground_truth.csv")
    if os.path.exists(test_truth):
        test_metrics = evaluate_predictions(test_preds, test_truth)
        print_evaluation(test_metrics)

    print(f"\n{'='*60}")
    print("  ✅ Pipeline complete!")
    print(f"  📂 Predictions: {test_output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

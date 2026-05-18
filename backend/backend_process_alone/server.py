import os
import sys

_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(_SERVER_DIR)
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

import shutil
import json
import ast
import tempfile
from pathlib import Path
from collections import Counter
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Pipeline imports ──────────────────────────────────────
from parsers.csv_loader import load_csv
from parsers.xml_to_csv import convert_xml_to_csv
from parsers.json_to_csv import convert_json_to_csv
from pipeline.preprocess import preprocess_invoice
from pipeline.predict import predict_invoice
from pipeline.correction import correct_invoice
from pipeline.mapper import map_invoice
from pipeline.append_transcode_history import append_transcode_history

import io

class DualStream(io.TextIOBase):
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.captured = io.StringIO()

    def write(self, s):
        self.original_stdout.write(s)
        self.captured.write(s)
        try:
            self.original_stdout.flush()
        except Exception:
            pass

    def flush(self):
        try:
            self.original_stdout.flush()
        except Exception:
            pass

    def getvalue(self):
        return self.captured.getvalue()

_pipeline_logs = "No pipeline has run in this session yet."

# =========================================================
app = FastAPI(title="E-Invoice Transcoder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://complyance-akry.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# ── Session gate ──────────────────────────────────────────
# All data endpoints return empty until the user uploads a
# file through the UI in this server session.
_pipeline_ready = False


# =========================================================
# HELPERS
# =========================================================

def _safe_read_csv(path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _error_breakdown(df: pd.DataFrame) -> list:
    counts: Counter = Counter()
    for val in df.get("mapping_errors", pd.Series(dtype=str)).dropna():
        for err in str(val).split(","):
            err = err.strip()
            if err:
                counts[err] += 1
    return [{"name": k, "value": v} for k, v in counts.most_common()]


def _severity(error: str) -> str:
    if error in {"tax_amount_mismatch", "missing_required_field", "buyer_vat_missing_for_target"}:
        return "High"
    if error in {"currency_not_supported", "seller_vat_format_invalid"}:
        return "Medium"
    return "Low"


def _not_ready():
    """Standard empty response when no file has been uploaded yet."""
    return None  # caller checks this


# =========================================================
# /api/health
# =========================================================

@app.get("/api/health")
def health():
    return {"status": "ok", "pipeline_ready": _pipeline_ready}


@app.get("/api/pipeline/logs")
def get_pipeline_logs():
    global _pipeline_logs
    return {"logs": _pipeline_logs}


# =========================================================
# /api/dashboard/summary
# =========================================================

@app.get("/api/dashboard/summary")
def dashboard_summary():
    if not _pipeline_ready:
        return {"ready": False}

    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
    if pred.empty:
        return {"ready": False}

    total = len(pred)
    valid_mask = pred["is_mapping_valid"].astype(str).isin(["1", "True", "true"])
    valid = int(valid_mask.sum())
    invalid = total - valid

    return {
        "ready": True,
        "totals": {
            "invoicesReceived": total,
            "invoicesValidated": valid,
            "invoicesTransformed": len(_safe_read_csv(OUTPUTS_DIR / "final_mapped_invoice.csv")),
            "successRate": round(valid / total * 100, 1) if total else 0,
            "exceptionRate": round(invalid / total * 100, 1) if total else 0,
            "averageProcessingTime": "N/A",
        },
        "validationSummary": [
            {"label": "Valid mappings", "value": round(valid / total * 100, 1) if total else 0},
            {"label": "Invalid mappings", "value": round(invalid / total * 100, 1) if total else 0},
        ],
    }


# =========================================================
# /api/dashboard/pipeline-stages
# =========================================================

@app.get("/api/dashboard/pipeline-stages")
def pipeline_stages():
    if not _pipeline_ready:
        return []
    return [
        {"name": "Ingestion",         "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "Pre-validation",    "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "Format resolution", "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "ML Prediction",     "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "Error correction",  "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "Transcoding",       "status": "completed", "throughput": 100, "latency": "—"},
        {"name": "Output generation", "status": "completed", "throughput": 100, "latency": "—"},
    ]


# =========================================================
# /api/dashboard/activity
# =========================================================

@app.get("/api/dashboard/activity")
def recent_activity():
    if not _pipeline_ready:
        return []

    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
    if pred.empty:
        return []

    recent = pred.tail(10).iloc[::-1]
    return [
        {
            "id": row.get("invoice_id", "—"),
            "status": "validated" if str(row.get("is_mapping_valid", "0")) in ("1", "True") else "flagged",
            "errors": str(row.get("mapping_errors", "")).strip(),
            "updatedAt": "Just now",
            "owner": "ML Engine",
        }
        for _, row in recent.iterrows()
    ]


# =========================================================
# /api/validation/results
# =========================================================

@app.get("/api/validation/results")
def validation_results():
    if not _pipeline_ready:
        return []

    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
    if pred.empty:
        return []

    invalid = pred[pred["is_mapping_valid"].astype(str).isin(["0", "False", "false"])]
    results = []
    for _, row in invalid.head(200).iterrows():
        errors_raw = str(row.get("mapping_errors", "")).strip()
        for err in [e.strip() for e in errors_raw.split(",") if e.strip()]:
            results.append({
                "invoice_id": row.get("invoice_id", "—"),
                "error_type": err.replace("_", " ").title(),
                "severity": _severity(err),
                "corrected_fields": err,
                "validation_status": "Corrected",
            })
    return results


# =========================================================
# /api/invoice/transformed
# =========================================================

@app.get("/api/invoice/transformed")
def transformed_invoice():
    if not _pipeline_ready:
        raise HTTPException(status_code=404, detail="No file uploaded yet. Use the Invoice Upload page.")

    mapped = _safe_read_csv(OUTPUTS_DIR / "final_mapped_invoice.csv").fillna("")
    corrected = _safe_read_csv(OUTPUTS_DIR / "corrected_invoice.csv").fillna("")
    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv").fillna("")

    if mapped.empty:
        raise HTTPException(status_code=404, detail="No transcoded invoice found.")

    # We return the top 50 invoices to prevent crashing the browser with massive JSON payloads
    invoices = []
    
    # Use invoice_id as key for fast lookups
    corr_dict = corrected.set_index("invoice_id").to_dict("index") if not corrected.empty and "invoice_id" in corrected.columns else {}
    pred_dict = pred.set_index("invoice_id").to_dict("index") if not pred.empty and "invoice_id" in pred.columns else {}
    
    limit = min(50, len(mapped))
    for i in range(limit):
        row = mapped.iloc[i].to_dict()
        inv_id = row.get("invoice_id")
        
        corr_row = corr_dict.get(inv_id, {})
        pred_row = pred_dict.get(inv_id, {})

        try:
            raw_lines = row.get("line_items.invoice_lines") or row.get("line_items") or "[]"
            if not raw_lines or str(raw_lines).strip() == "":
                raw_lines = "[]"
            line_items = ast.literal_eval(str(raw_lines))
        except Exception:
            line_items = []

        invoices.append({
            "invoice_id": str(inv_id),
            "target_format": str(row.get("target_format", "—")),
            "source_format": str(row.get("syntax", "—")),
            "target_country": str(row.get("target_country", "—")),
            "transformation_status": "Completed",
            "totals": {
                "subtotal": row.get("subtotal", 0) if row.get("subtotal") else 0,
                "tax": row.get("tax_amount", 0) if row.get("tax_amount") else 0,
                "grand_total": row.get("total_amount", 0) if row.get("total_amount") else 0,
                "currency": str(row.get("currency", "EUR")),
            },
            "parties": {
                "seller": {"id": str(row.get("seller_id", "—")), "vat": str(row.get("seller_vat", "—"))},
                "buyer": {"id": str(row.get("buyer_id", "—")), "vat": str(row.get("buyer_vat", "—"))},
            },
            "dates": {
                "issue_date": str(row.get("issue_date", "—")),
                "delivery_date": str(row.get("delivery_date", "—")),
            },
            "payment_reference": str(row.get("payment_reference", "—")),
            "line_items": line_items[:10] if isinstance(line_items, list) else [],
            "metadata": {
                "corrected_fields": str(corr_row.get("corrected_fields", "{}")),
                "mapping_valid": str(pred_row.get("is_mapping_valid", "1")) in ("1", "True"),
                "mapping_errors": str(pred_row.get("mapping_errors", "")),
            },
        })

    return {
        "total_transformed": len(mapped),
        "showing": limit,
        "invoices": invoices
    }


# =========================================================
# /api/analytics/summary
# =========================================================

@app.get("/api/analytics/summary")
def analytics_summary():
    if not _pipeline_ready:
        return {}

    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
    if pred.empty:
        return {}

    total = len(pred)
    valid_mask = pred["is_mapping_valid"].astype(str).isin(["1", "True", "true"])
    invalid = int((~valid_mask).sum())

    error_breakdown = _error_breakdown(pred)
    severity_map = {"High": 0, "Medium": 0, "Low": 0}
    for item in error_breakdown:
        severity_map[_severity(item["name"])] += item["value"]

    return {
        "throughput": [{"name": "Uploaded batch", "invoices": total, "errors": invalid}],
        "severityBreakdown": [{"name": k, "value": v} for k, v in severity_map.items()],
        "errorBreakdown": error_breakdown,
        "countryMix": [],
    }


# =========================================================
# /api/audit/logs
# =========================================================

@app.get("/api/audit/logs")
def audit_logs():
    if not _pipeline_ready:
        return []

    pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
    if pred.empty:
        return []

    logs = []
    for i, (_, row) in enumerate(pred.iterrows()):
        is_valid = str(row.get("is_mapping_valid", "1")) in ("1", "True")
        errors = str(row.get("mapping_errors", "")).strip()
        logs.append({
            "id": i + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": "ML Validator" if is_valid else "Correction Engine",
            "event": "Validation passed" if is_valid else "Validation failed",
            "target": row.get("invoice_id", f"INV-{i}"),
            "details": (
                "Passed all mapping checks."
                if is_valid
                else f"Errors: {errors}. Correction applied."
            ),
        })
    return logs[:100]


# =========================================================
# /api/invoice/upload  —  THE MAIN PIPELINE TRIGGER
# =========================================================

@app.post("/api/invoice/upload")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Accept a CSV / JSON / XML invoice file, run the full 5-stage
    pipeline, and unlock all dashboard endpoints.
    """
    global _pipeline_ready, _pipeline_logs

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in ("csv", "json", "xml"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    import sys
    dual_stream = DualStream(sys.stdout)
    old_stdout = sys.stdout
    sys.stdout = dual_stream

    try:
        print(f"\nDetected File Type : {ext}")

        # Stage 1 — Parse
        if ext == "xml":
            print("\nConverting XML to CSV...")
            csv_path = convert_xml_to_csv(tmp_path)
        elif ext == "json":
            print("\nConverting JSON to CSV...")
            csv_path = convert_json_to_csv(tmp_path)
        else:
            print("\nLoading CSV file...")
            csv_path = load_csv(tmp_path)

        print(f"\nCSV Ready : {csv_path}")

        # Stage 2 — Preprocess
        print("\nStarting preprocessing pipeline...")
        processed_df = preprocess_invoice(csv_path)
        print("\nPreprocessing completed.")

        # Stage 3 — ML Predict
        print("\nRunning model prediction...")
        predict_invoice(processed_df, csv_path)
        print("\nPrediction completed.")

        # Stage 4 — Correct
        print("\nStarting correction engine...")
        correct_invoice(csv_path, "outputs/prediction_output.csv")
        print("\nCorrection completed.")

        # Stage 5 — Transcode / Map
        print("\nStarting invoice transcoding...")
        map_invoice("outputs/corrected_invoice.csv", ext)
        print("\nTranscoding completed.")

        # Stage 6 — Append Transcode History to PostgreSQL
        print("\nAppending transcode history into PostgreSQL...")
        append_transcode_history(csv_path, "outputs/corrected_invoice.csv", "outputs/prediction_output.csv")
        print("\nTranscode history append completed.")

        print("\nPipeline Completed Successfully.")

        # ── Unlock all dashboard endpoints ─────────────────
        _pipeline_ready = True

        pred = _safe_read_csv(OUTPUTS_DIR / "prediction_output.csv")
        total = len(pred)
        valid_mask = pred["is_mapping_valid"].astype(str).isin(["1", "True", "true"])
        valid = int(valid_mask.sum())
        invalid = total - valid

        return {
            "fileName": file.filename,
            "status": "Pipeline completed",
            "accepted": True,
            "summary": {
                "totalInvoices": total,
                "validMappings": valid,
                "invalidMappings": invalid,
                "successRate": round(valid / total * 100, 1) if total else 0,
            },
            "warnings": [
                f"Processed {total} invoices",
                f"{valid} valid ({round(valid/total*100,1) if total else 0}%)",
                f"{invalid} errors detected and auto-corrected",
            ],
            "outputs": [
                "outputs/prediction_output.csv",
                "outputs/corrected_invoice.csv",
                "outputs/final_mapped_invoice.csv",
            ],
            "terminal_logs": dual_stream.getvalue(),
        }

    except Exception as e:
        print(f"\nPipeline Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        sys.stdout = old_stdout
        _pipeline_logs = dual_stream.getvalue()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

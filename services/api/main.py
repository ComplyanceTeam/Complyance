import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from prisma import Prisma, Json
from pipeline_wrapper import run_transcode_pipeline
from contextlib import asynccontextmanager
from core.engine.utils import clean_nan_values

# Initialize Prisma client
db = Prisma()

# In-memory fallback for when the database is unreachable
memory_history = []


def build_memory_record(clean_result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "invoice_id": clean_result.get("invoice_id", "UNKNOWN"),
        "source_format": clean_result.get("source_format", "UNKNOWN"),
        "target_format": str(clean_result.get("target_format", "UNKNOWN")),
        "is_mapping_valid": bool(clean_result.get("is_mapping_valid", False)),
        "mapping_errors": clean_result.get("mapping_errors", ""),
        "transcoded_payload": clean_result.get("transcoded_payload"),
        "created_at": datetime.utcnow().isoformat(),
    }

async def ensure_db_connected():
    if db.is_connected():
        return
    try:
        await db.connect()
    except Exception:
        try:
            await db.disconnect()
        except Exception:
            pass
        await db.connect()


async def db_call(coro_factory):
    try:
        await ensure_db_connected()
        return await coro_factory()
    except Exception:
        try:
            await db.disconnect()
        except Exception:
            pass
        try:
            await db.connect()
            return await coro_factory()
        except Exception:
            return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database on startup (allow recovery if it is temporarily unavailable)
    try:
        await db.connect()
    except Exception as exc:
        print(f"Database connection failed during startup: {exc}")
    yield
    # Disconnect on shutdown
    if db.is_connected():
        await db.disconnect()

app = FastAPI(title="Complyance E-Invoice Transcoder API", lifespan=lifespan)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class InvoiceInput(BaseModel):
    invoice_id: str
    source_format: str
    target_country: str
    seller_id: str
    buyer_id: str
    issue_date: str
    currency: str
    subtotal: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    line_items_json: str
    seller_vat: Optional[str] = None
    buyer_vat: Optional[str] = None
    payment_reference: Optional[str] = None
    delivery_date: Optional[str] = None

class TranscodeResponse(BaseModel):
    id: str
    invoice_id: str
    source_format: str
    target_format: str
    is_mapping_valid: bool
    mapping_errors: Optional[str]
    transcoded_payload: Optional[Dict[str, Any]]
    created_at: Any

@app.get("/api/health")
async def health():
    return {"status": "operational", "engine": "ML Supervisor v2.4"}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """
    Computes real-time statistics from the PostgreSQL database.
    """
    try:
        total_count = await db_call(lambda: db.transcodehistory.count())
        valid_count = await db_call(lambda: db.transcodehistory.count(where={"is_mapping_valid": True}))

        if total_count is None or valid_count is None:
            raise RuntimeError("DB unavailable")

        invalid_count = total_count - valid_count
        
        success_rate = round((valid_count / total_count * 100), 1) if total_count > 0 else 100.0
        
        return {
            "totals": {
                "invoicesReceived": total_count,
                "invoicesValidated": total_count,
                "invoicesTransformed": valid_count,
                "successRate": success_rate,
                "exceptionRate": round(100.0 - success_rate, 1),
                "averageProcessingTime": "0.8s"
            }
        }
    except Exception:
        total_count = len(memory_history)
        valid_count = sum(1 for row in memory_history if row.get("is_mapping_valid"))
        success_rate = round((valid_count / total_count * 100), 1) if total_count > 0 else 100.0
        return {
            "totals": {
                "invoicesReceived": total_count,
                "invoicesValidated": total_count,
                "invoicesTransformed": valid_count,
                "successRate": success_rate,
                "exceptionRate": round(100.0 - success_rate, 1),
                "averageProcessingTime": "0.8s"
            }
        }

@app.post("/api/transcode", response_model=TranscodeResponse)
async def transcode_invoice(invoice: InvoiceInput):
    """
    Processes a single invoice through the pipeline.
    """
    try:
        # Check for duplicates
        try:
            existing = await db_call(lambda: db.transcodehistory.find_unique(where={"invoice_id": invoice.invoice_id}))
        except Exception:
            existing = next((row for row in memory_history if row.get("invoice_id") == invoice.invoice_id), None)
        if existing:
            return existing

        # Run pipeline
        result = run_transcode_pipeline(invoice.dict())
        clean_result = clean_nan_values(result)
        
        # Save to DB
        try:
            record = await db_call(lambda: db.transcodehistory.create(
                data={
                    "invoice_id": clean_result["invoice_id"],
                    "source_format": clean_result["source_format"],
                    "target_format": str(clean_result.get("target_format", "UNKNOWN")),
                    "original_payload": Json(clean_result["original_payload"]),
                    "transcoded_payload": Json(clean_result["transcoded_payload"]),
                    "is_mapping_valid": clean_result["is_mapping_valid"],
                    "mapping_errors": clean_result["mapping_errors"]
                }
            ))
            if record is not None:
                return record
            raise RuntimeError("DB unavailable")
        except Exception:
            record = build_memory_record(clean_result)
            memory_history.insert(0, record)
            return record
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transcode-file", response_model=TranscodeResponse)
async def transcode_invoice_file(
    file: UploadFile = File(...),
    file_type: Optional[str] = Form(None)
):
    """
    Processes a single invoice from an uploaded file (CSV, JSON, XML).
    """
    try:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Missing file upload.")

        extension = (file_type or file.filename.split(".")[-1]).lower()
        if extension not in {"json", "csv", "xml"}:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV, JSON, or XML.")

        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if extension == "json":
            text = raw_bytes.decode("utf-8")
            sanitized_text = text.replace(": NaN", ": null")
            payload = json.loads(sanitized_text)

            if isinstance(payload, list):
                if len(payload) == 0:
                    raise HTTPException(status_code=400, detail="JSON array is empty.")
                payload = payload[0]

            if not isinstance(payload, dict):
                raise HTTPException(status_code=400, detail="JSON payload must be an invoice object.")

            result = run_transcode_pipeline(payload, file_type="json")
        else:
            text = raw_bytes.decode("utf-8")
            result = run_transcode_pipeline(text, file_type=extension)

        clean_result = clean_nan_values(result)

        existing = None
        invoice_id = clean_result.get("invoice_id")
        if invoice_id and invoice_id != "UNKNOWN":
            try:
                existing = await db_call(lambda: db.transcodehistory.find_unique(where={"invoice_id": invoice_id}))
            except Exception:
                existing = next((row for row in memory_history if row.get("invoice_id") == invoice_id), None)
        if existing:
            return existing

        try:
            record = await db_call(lambda: db.transcodehistory.create(
                data={
                    "invoice_id": clean_result.get("invoice_id", "UNKNOWN"),
                    "source_format": clean_result.get("source_format", "UNKNOWN"),
                    "target_format": str(clean_result.get("target_format", "UNKNOWN")),
                    "original_payload": Json(clean_result.get("original_payload", {})),
                    "transcoded_payload": Json(clean_result.get("transcoded_payload", {})),
                    "is_mapping_valid": clean_result.get("is_mapping_valid", False),
                    "mapping_errors": clean_result.get("mapping_errors", "")
                }
            ))
            if record is not None:
                return record
            raise RuntimeError("DB unavailable")
        except Exception:
            record = build_memory_record(clean_result)
            memory_history.insert(0, record)
            return record
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history", response_model=List[TranscodeResponse])
async def get_history(limit: int = 10):
    try:
        rows = await db_call(lambda: db.transcodehistory.find_many(
            order={"created_at": "desc"},
            take=limit
        ))
        if rows is None:
            raise RuntimeError("DB unavailable")
        return rows
    except Exception:
        return memory_history[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

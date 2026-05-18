import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from prisma import Prisma
from pipeline_wrapper import run_transcode_pipeline
from contextlib import asynccontextmanager
from core.engine.utils import clean_nan_values

# Initialize Prisma client
db = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database on startup
    await db.connect()
    yield
    # Disconnect on shutdown
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
        total_count = await db.transcodehistory.count()
        valid_count = await db.transcodehistory.count(where={"is_mapping_valid": True})
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
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/transcode", response_model=TranscodeResponse)
async def transcode_invoice(invoice: InvoiceInput):
    """
    Processes a single invoice through the pipeline.
    """
    try:
        # Check for duplicates
        existing = await db.transcodehistory.find_unique(where={"invoice_id": invoice.invoice_id})
        if existing:
            return existing

        # Run pipeline
        result = run_transcode_pipeline(invoice.dict())
        clean_result = clean_nan_values(result)
        
        # Save to DB
        record = await db.transcodehistory.create(
            data={
                "invoice_id": clean_result["invoice_id"],
                "source_format": clean_result["source_format"],
                "target_format": clean_result["target_format"],
                "original_payload": clean_result["original_payload"],
                "transcoded_payload": clean_result["transcoded_payload"],
                "is_mapping_valid": clean_result["is_mapping_valid"],
                "mapping_errors": clean_result["mapping_errors"]
            }
        )
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history", response_model=List[TranscodeResponse])
async def get_history(limit: int = 10):
    try:
        return await db.transcodehistory.find_many(
            order={"created_at": "desc"},
            take=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

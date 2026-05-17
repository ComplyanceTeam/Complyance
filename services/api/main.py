import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from prisma import Prisma
from pipeline_wrapper import run_transcode_pipeline
from contextlib import asynccontextmanager

# Initialize Prisma client
db = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database on startup
    await db.connect()
    yield
    # Disconnect on shutdown
    await db.disconnect()

app = FastAPI(title="E-Invoice Transcoder API", lifespan=lifespan)

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

@app.post("/api/transcode", response_model=TranscodeResponse)
async def transcode_invoice(invoice: InvoiceInput):
    """
    Processes an invoice through the ML pipeline and saves the result to PostgreSQL.
    """
    try:
        # 1. Run the pipeline
        result = run_transcode_pipeline(invoice.dict())
        
        # 2. Save to Database
        record = await db.transcodehistory.create(
            data={
                "invoice_id": result["invoice_id"],
                "source_format": result["source_format"],
                "target_format": result["target_format"],
                "original_payload": result["original_payload"],
                "transcoded_payload": result["transcoded_payload"],
                "is_mapping_valid": result["is_mapping_valid"],
                "mapping_errors": result["mapping_errors"]
            }
        )
        
        return {
            "id": record.id,
            "invoice_id": record.invoice_id,
            "source_format": record.source_format,
            "target_format": record.target_format,
            "is_mapping_valid": record.is_mapping_valid,
            "mapping_errors": record.mapping_errors,
            "transcoded_payload": result["transcoded_payload"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history", response_model=List[TranscodeResponse])
async def get_history(limit: int = 10):
    """
    Retrieves the most recent transcoding history from the database.
    """
    try:
        records = await db.transcodehistory.find_many(
            order={"created_at": "desc"},
            take=limit
        )
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

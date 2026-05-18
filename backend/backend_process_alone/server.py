import os
from parsers.xml_to_csv import convert_xml_to_csv
from parsers.json_to_csv import convert_json_to_csv
from parsers.csv_loader import load_csv
from pipeline.preprocess import preprocess_invoice
from pipeline.predict import predict_invoice
from pipeline.correction import correct_invoice
from pipeline.mapper import map_invoice
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

@app.post("/process-invoice")
async def process_invoice(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Detect file type and process
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension == 'xml':
            csv_path = convert_xml_to_csv(file_location)
        elif file_extension == 'json':
            csv_path = convert_json_to_csv(file_location)
        elif file_extension == 'csv':
            csv_path = load_csv(file_location)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # Run pipeline
        processed_df = preprocess_invoice(csv_path)
        prediction_output = predict_invoice(processed_df, csv_path)
        corrected_df = correct_invoice(csv_path, 'outputs/prediction_output.csv')
        mapped_df = map_invoice('outputs/corrected_invoice.csv', file_extension)

        # Save final output to database (example)
        mapped_df.to_sql('processed_invoices', con=engine, if_exists='append', index=False)

        return JSONResponse(content={"message": "Invoice processed successfully."})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    try:
        # Fetch results from database
        query = "SELECT * FROM processed_invoices ORDER BY id DESC LIMIT 10"
        results = pd.read_sql(query, con=engine)
        return JSONResponse(content=results.to_dict(orient='records'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
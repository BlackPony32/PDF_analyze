# FastAPI main file

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import logging
import numpy as np
from pdf_maker import generate_pdf  # Import the PDF generation logic

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5000",  # Flask server URL
    "http://127.0.0.1:5000"   # Another form of localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_data(data):
    """
    Convert non-JSON compliant values to strings.
    """
    def convert_value(value):
        if isinstance(value, float) and (value == float('inf') or value == float('-inf') or np.isnan(value)):
            return str(value)
        return value

    return [{key: convert_value(value) for key, value in row.items()} for row in data]

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")

    # Check if the file has a valid extension
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV, XLSX, and XLS are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    try:
        # Process the file with pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')  # Specify the engine for .xlsx files
        elif file.filename.endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')  # Specify the engine for .xls files

        # Generate sanitized data for JSON response
        data = sanitize_data(df.to_dict(orient='records'))

        # Generate the PDF
        pdf_path = generate_pdf(df, file.filename)  # Ensure it returns a PDF path
        pdf_url = f"/download/{os.path.basename(pdf_path)}"

        return JSONResponse(content={"message": "File processed successfully", "data": data, "pdf_url": pdf_url})
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = os.path.join(PDF_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(file_path, media_type='application/pdf', filename=filename)

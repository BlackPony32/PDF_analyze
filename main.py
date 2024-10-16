import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import logging
import numpy as np
from additional_functions.pdf_maker import generate_pdf  # Import the PDF generation logic
from additional_functions.preprocess_data import preprocess_data
#from AI_instruments import ai_main
from AI_instruments.one_agent_main import AI_generation_plots_summary
from AI_instruments.final_sum import final_gen
from pathlib import Path


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

# Configure logging to write to a file
log_file_path = "preprocess_log.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Define the upload and PDF folders
UPLOAD_FOLDER = 'src/uploads'
PDF_FOLDER = 'src/pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

def convert_excel_to_csv(excel_file_path):
    try:
        df = pd.read_excel(excel_file_path)
        csv_file_path = os.path.splitext(excel_file_path)[0] + ".csv"
        df.to_csv(csv_file_path, index=False)
        os.remove(excel_file_path)
        return csv_file_path
    except Exception as e:
        raise ValueError(f"Error converting Excel to CSV: {str(e)}")

def clean_directories():
    plots_folder = 'src/plots'
    summary_folder = 'src/summary'
    
    # Remove all files in the 'plots' folder
    if os.path.exists(plots_folder):
        for filename in os.listdir(plots_folder):
            file_path = os.path.join(plots_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file {file_path} from plots folder")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
    
    # Remove all files in the 'summary' folder
    if os.path.exists(summary_folder):
        for filename in os.listdir(summary_folder):
            file_path = os.path.join(summary_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file {file_path} from summary folder")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")

@app.post("/src/upload")
async def upload_file(file: UploadFile = File(...)):
    # Ensure folders exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)

    # Check if the file has a valid extension
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        logger.error("Invalid file format uploaded.")
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV, XLSX, and XLS are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        logger.info(f"Uploaded file {file.filename} to {UPLOAD_FOLDER}")

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path, low_memory=False)
        elif file.filename.endswith('.xlsx'):
            excel_file_path = f"{UPLOAD_FOLDER}/{file.filename}"
            file_path = convert_excel_to_csv(excel_file_path)
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Converted Excel to CSV and loaded file: {file.filename}")
        elif file.filename.endswith('.xls'):
            excel_file_path = f"{UPLOAD_FOLDER}/{file.filename}"
            file_path = convert_excel_to_csv(excel_file_path)
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"Converted Excel to CSV and loaded file: {file.filename}")
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")
    
    try:
        # Generate plots and summarize data
        path = Path(file_path)  #example "src/uploads\\ideal_short.csv"
        filename = path.name
        action = preprocess_data(path)
        logger.info(f"Generating plots for file: {filename}")
        
        cleaned_dataset_name = "cleaned_data.csv"
        AI_generation_plots_summary(cleaned_dataset_name)
        logger.info("Plot generation completed")

        final_gen(f"src/uploads/{filename}")  # Ensure this function generates a summary
        logger.info("Data summary generated")

        # Generate the PDF
        pdf_path = generate_pdf(filename)  # Ensure it returns a PDF path
        logger.info(f"Generated PDF at {pdf_path}")

        pdf_url = f"/download/{os.path.basename(pdf_path)}"

        #clean_directories()  # Clean temporary directories after processing
        return JSONResponse(content={"message": "File processed successfully","action":action, "pdf_url": pdf_url})

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = os.path.join(PDF_FOLDER, filename)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found.")
    
    logger.info(f"Downloading PDF: {filename}")
    return FileResponse(file_path, media_type='application/pdf', filename=filename)

# Run the Uvicorn server with custom logger configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
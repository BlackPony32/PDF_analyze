from temp import extract_main_info
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import logging
import numpy as np
from short_ai_test import AI_generation_plots_summary1
from additional_functions.pdf_maker import generate_pdf  # Import the PDF generation logic
from additional_functions.preprocess_data import preprocess_data
#from AI_instruments import ai_main
#from AI_instruments.final_sum import final_gen
from pathlib import Path

app = FastAPI()
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

@app.post("/users_file")
async def upload_file(file: UploadFile = File(...)):
    
    # Check if the file has a valid extension
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV, XLSX, and XLS are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path, low_memory=False)
        elif file.filename.endswith('.xlsx'):
            excel_file_path = f"{UPLOAD_FOLDER}/{file.filename}"
            file_path = convert_excel_to_csv(excel_file_path)
            df = pd.read_csv(file_path, low_memory=False)
        elif file.filename.endswith('.xls'):
            excel_file_path = f"{UPLOAD_FOLDER}/{file.filename}"
            file_path = convert_excel_to_csv(excel_file_path)
            df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")
    
    try:
        # Generate plots and summarize data
        path = Path(file_path)  #example "src/uploads\\ideal_short.csv"
        filename = path.name
        
        action = preprocess_data(path)
        
        try:
            cleaned_dataset_name = "src/uploads/cleaned_data.csv"
            _df = pd.read_csv(cleaned_dataset_name, low_memory=False)
            data_dict = extract_main_info(_df)
        except Exception as e:
            print(f'here 1 :{e}')
        try:
            
            AI_generation_plots_summary1(data_dict, cleaned_dataset_name)
            #final_gen(f"src/uploads/{filename}")  # Ensure this function generates a summary
        except Exception as e:
            print(f'here 2 :{e}')
        # Generate the PDF
        pdf_path = generate_pdf(filename)  # Ensure it returns a PDF path
        pdf_url = f"/download/{os.path.basename(pdf_path)}"

        #clean_directories()  # Clean temporary directories after processing
        return JSONResponse(content={"message": "File processed successfully","action":action, "pdf_url": pdf_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

    
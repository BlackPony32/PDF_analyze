from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.responses import JSONResponse
import pandas as pd
import os
import logging
import numpy as np

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    return [{k: convert_value(v) for k, v in row.items()} for row in data]

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        logger.error(f"File type not allowed: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are allowed.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        # Stream and save the file
        with open(file_path, 'wb') as f:
            while True:
                chunk = await file.read(1024 * 1024)  # Read in 1MB chunks
                if not chunk:
                    break
                f.write(chunk)

        file_extension = file.filename.rsplit('.', 1)[1].lower()

        # Process the file
        if file_extension in {'csv'}:
            df = pd.read_csv(file_path)
        elif file_extension in {'xlsx', 'xls'}:
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are allowed.")

        # Convert to dictionary format and sanitize data
        data = df.to_dict(orient='records')
        sanitized_data = sanitize_data(data)

        return {"message": "File processed successfully", "data": sanitized_data}

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return JSONResponse(content={"message": f"There was an error uploading the file: {str(e)}"}, status_code=500)
    finally:
        await file.close()

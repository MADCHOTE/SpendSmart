from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from file_parser import parse_pdf, parse_csv, parse_image
from database import init_db, save_upload, get_all_uploads
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database when app starts!
init_db()

# Serve static files (our frontend!)
app.mount("/static", StaticFiles(directory="static"), 
          name="static")

# Home route → serve index.html!
@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()

    if file.filename.endswith('.pdf'):
        result = parse_pdf(contents)
        file_type = 'pdf'

    elif file.filename.endswith('.csv'):
        result = parse_csv(contents)
        file_type = 'csv'

    elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
        result = parse_image(contents)
        file_type = 'image'

    else:
        return {"error": "Unsupported file type!"}

    transactions = result['transactions']
    upload_id = save_upload(
        file.filename,
        file_type,
        transactions
    )

    return {
        "message": "File processed successfully! ✅",
        "file_name": file.filename,
        "upload_id": upload_id,
        "data": result
    }

@app.get("/history")
def get_history():
    uploads = get_all_uploads()
    return {"uploads": uploads}

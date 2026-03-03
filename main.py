from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from file_parser import parse_pdf, parse_csv, parse_image
from database import init_db, save_upload, get_all_uploads

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database when app starts!
init_db()


@app.get("/")
def home():
    return {"message": "SpendSmart is alive! 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()

    # Parse based on file type
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

    # Save to database!
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


# New endpoint to get upload history!
@app.get("/history")
def get_history():
    uploads = get_all_uploads()
    return {
        "uploads": uploads
    }

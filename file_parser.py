import fitz  # PyMuPDF
from ai_extractor import extract_transactions_with_ai


def parse_pdf(file_bytes):
    """
    Reads PDF and extracts raw text
    Sends to AI for intelligent extraction
    """
    # Open PDF
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    # Extract all text
    raw_text = ""
    for page in pdf:
        raw_text += page.get_text()

    print("✅ PDF text extracted successfully!")
    print(f"📄 Total characters: {len(raw_text)}")

    # Send to AI extractor
    transactions = extract_transactions_with_ai(raw_text)

    return {"transactions": transactions}


def parse_csv(file_bytes):
    """
    Reads CSV file smartly
    Sends to AI for extraction
    """
    import pandas as pd
    import io

    # Read CSV into pandas dataframe
    raw_text = file_bytes.decode("utf-8")
    
    try:
        # Try reading as proper CSV
        df = pd.read_csv(io.StringIO(raw_text))
        
        print(f"✅ CSV loaded! Columns: {list(df.columns)}")
        print(f"📄 Rows: {len(df)}")
        print(df.head())
        
        # Convert dataframe to clean text for AI
        formatted_text = df.to_string(index=False)
        
    except Exception as e:
        print(f"⚠️ Pandas failed, using raw text: {e}")
        formatted_text = raw_text

    print("✅ CSV text extracted successfully!")

    # Send to AI extractor
    transactions = extract_transactions_with_ai(formatted_text)

    return {"transactions": transactions}


def parse_image(file_bytes):
    def parse_image(file_bytes):
    """
    Reads text from screenshot using OCR
    Sends to AI for extraction
    """
    try:
        import pytesseract
        from PIL import Image
        import io

        # Only set this path on Windows!
        import platform
        if platform.system() == "Windows":
            pytesseract.pytesseract.tesseract_cmd = (
                r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            )

        image = Image.open(io.BytesIO(file_bytes))
        print(f"✅ Image loaded! Size: {image.size}")

        raw_text = pytesseract.image_to_string(image)
        print(f"✅ OCR extracted: {raw_text[:100]}")

        transactions = extract_transactions_with_ai(raw_text)
        return {"transactions": transactions}

    except Exception as e:
        print(f"⚠️ OCR failed: {str(e)}")
        return {
            "transactions": [],
            "message": "OCR not available on this server!"
        }
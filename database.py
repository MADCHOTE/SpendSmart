import sqlite3
import json
from datetime import datetime

# Database file will be created automatically
# in your SpendSmart folder!
DB_FILE = "spendsmart.db"


def init_db():
    """
    Creates database tables if they don't exist
    Called once when app starts!
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create uploads table
    # Each upload = one row
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_type TEXT,
            upload_date TEXT,
            total_amount REAL,
            total_transactions INTEGER
        )
    ''')

    # Create transactions table
    # Each transaction = one row
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            description TEXT,
            amount REAL,
            category TEXT,
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized!")


def save_upload(filename, file_type, transactions):
    """
    Saves an upload and all its transactions
    to the database!
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Calculate totals
    total_amount = sum(t['amount'] for t in transactions)
    total_transactions = len(transactions)

    # Save upload record
    cursor.execute('''
        INSERT INTO uploads 
        (filename, file_type, upload_date, 
         total_amount, total_transactions)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        filename,
        file_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_amount,
        total_transactions
    ))

    # Get the upload id we just created
    upload_id = cursor.lastrowid

    # Save each transaction
    for t in transactions:
        cursor.execute('''
            INSERT INTO transactions
            (upload_id, description, amount, category)
            VALUES (?, ?, ?, ?)
        ''', (
            upload_id,
            t['description'],
            t['amount'],
            t['category']
        ))

    conn.commit()
    conn.close()

    print(f"✅ Saved to database! Upload ID: {upload_id}")
    return upload_id


def get_all_uploads():
    """
    Returns all past uploads
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM uploads
        ORDER BY upload_date DESC
    ''')

    uploads = cursor.fetchall()
    conn.close()

    return [
        {
            "id": u[0],
            "filename": u[1],
            "file_type": u[2],
            "upload_date": u[3],
            "total_amount": u[4],
            "total_transactions": u[5]
        }
        for u in uploads
    ]


def get_upload_transactions(upload_id):
    """
    Returns all transactions for a specific upload
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM transactions
        WHERE upload_id = ?
    ''', (upload_id,))

    transactions = cursor.fetchall()
    conn.close()

    return [
        {
            "id": t[0],
            "upload_id": t[1],
            "description": t[2],
            "amount": t[3],
            "category": t[4]
        }
        for t in transactions
    ]
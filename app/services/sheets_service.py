import urllib.request
import csv
import io
import sqlite3
import os
import threading
import time
import schedule

# Cloud spreadsheet access URL
SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSnt8fXWYKBgRag9tf2NbKc6OLmkGac4JqAjyjWLcCrT250UEb1s3y7x_JgBmUE0cgZ1MnB_7CAyG/pub?gid=0&single=true&output=csv'

# Absolute path alignment for local SQLite engine instances
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'library_offline.db')

IS_RENDER_CLOUD = 'RENDER' in os.environ

def init_local_db():
    """Initializes local database infrastructure file on desktop machines."""
    if IS_RENDER_CLOUD:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            category TEXT,
            status TEXT,
            borrowed_by TEXT,
            level_section TEXT,
            date_borrowed TEXT,
            due_date TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_local_db()

def process_and_sanitize_row(row):
    """Cleans up rows altered by Google Sheets dropdown formatting and returns exactly 9 elements."""
    # Step 1: Pad with empty strings if the row is somehow too short
    while len(row) < 9:
        row.append("")
    
    # Step 2: Extract exactly the first 9 key column fields (bypasses dropdown artifacts)
    clean_row = [
        str(row[0]).strip(),  # Lexil Level / ID
        str(row[1]).strip(),  # Title
        str(row[2]).strip(),  # Author
        str(row[3]).strip(),  # Category
        str(row[4]).strip(),  # Status
        str(row[5]).strip(),  # Borrowed By
        str(row[6]).strip(),  # Level & Section
        str(row[7]).strip(),  # Date Borrowed
        str(row[8]).strip()   # Due Date
    ]
    return clean_row

def fetch_direct_from_google_sheets():
    """Fallback engine streaming real-time spreadsheet mutations when cloud-hosted."""
    books_list = []
    try:
        response = urllib.request.urlopen(SHEET_CSV_URL, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if not rows or len(rows) <= 1:
            return []

        for row in rows[1:]:
            if not row or not row[0].strip():
                continue  # Skip blank spacer rows safely
                
            clean = process_and_sanitize_row(row)
            books_list.append({
                'id': clean[0], 'title': clean[1], 'author': clean[2],
                'category': clean[3], 'status': clean[4], 'borrowed_by': clean[5],
                'level_section': clean[6], 'date_borrowed': clean[7], 'due_date': clean[8]
            })
    except Exception as e:
        print(f"[❌ Cloud Error] Real-time live data stream failed: {e}")
    return books_list

def pull_remote_to_local():
    """Pulls sheet mutations downstream and safely caches them into the local database."""
    if IS_RENDER_CLOUD:
        return False
    try:
        response = urllib.request.urlopen(SHEET_CSV_URL, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if not rows or len(rows) <= 1:
            return False

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for row in rows[1:]:
            if not row or not row[0].strip():
                continue  # Bypasses dangling rows outside inventory scope
                
            clean = process_and_sanitize_row(row)
            
            cursor.execute('''
                INSERT INTO books (id, title, author, category, status, borrowed_by, level_section, date_borrowed, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title, author=excluded.author, category=excluded.category,
                    status=excluded.status, borrowed_by=excluded.borrowed_by, 
                    level_section=excluded.level_section, date_borrowed=excluded.date_borrowed, due_date=excluded.due_date
            ''', tuple(clean))
            
        conn.commit()
        conn.close()
        print("[⚡ Local Sync] Cloud records cached locally successfully.")
        return True
    except Exception as e:
        print(f"[❌ Sync Offline Warning] Offline mode operational: {e}")
        return False

def get_live_books_data():
    """Extracts catalog listings via high-speed SQLite local memory tables."""
    if IS_RENDER_CLOUD:
        return fetch_direct_from_google_sheets()

    books_list = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books')
        rows = cursor.fetchall()
        for row in rows:
            books_list.append({
                'id': row['id'], 'title': row['title'], 'author': row['author'],
                'category': row['category'], 'status': row['status'], 'borrowed_by': row['borrowed_by'],
                'level_section': row['level_section'], 'date_borrowed': row['date_borrowed'], 'due_date': row['due_date']
            })
        conn.close()
    except Exception as e:
        print(f"[❌ Database Error] Data parsing failed: {e}")
    
    if not books_list:
        pull_remote_to_local()
        # Fallback quick-read validation pass
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books')
            books_list = [{ 'id': r['id'], 'title': r['title'], 'author': r['author'], 'category': r['category'], 'status': r['status'], 'borrowed_by': r['borrowed_by'], 'level_section': r['level_section'], 'date_borrowed': r['date_borrowed'], 'due_date': r['due_date'] } for r in cursor.fetchall()]
            conn.close()
        except: pass
        
    return books_list

def run_sync_schedule():
    if IS_RENDER_CLOUD:
        return
    schedule.every(2).minutes.do(pull_remote_to_local)
    pull_remote_to_local()
    while True:
        schedule.run_pending()
        time.sleep(1)

if not IS_RENDER_CLOUD:
    sync_thread = threading.Thread(target=run_sync_schedule, daemon=True)
    sync_thread.start()

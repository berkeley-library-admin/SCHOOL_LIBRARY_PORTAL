import urllib.request
import csv
import io
import sqlite3
import os
import threading
import time
import schedule

# Corrected, non-truncated cloud spreadsheet access pipeline URL
SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSnt8fXWYKBgRag9tf2NbKc6OLmkGac4JqAjyjWLcCrT250UEb1s3y7x_JgBmUE0cgZ1MnB_7CAyG/pub?gid=0&single=true&output=csv'

# Absolute path alignment matrix for local SQLite engine instances
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

def fetch_direct_from_google_sheets():
    """Fallback engine streaming real-time spreadsheet mutations when cloud-hosted."""
    books_list = []
    try:
        response = urllib.request.urlopen(SHEET_CSV_URL, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if not rows:
            return []

        for row in rows[1:]:
            while len(row) < 9:
                row.append("")
            books_list.append({
                'id': row[0], 'title': row[1], 'author': row[2],
                'category': row[3], 'status': row[4], 'borrowed_by': row[5],
                'level_section': row[6], 'date_borrowed': row[7], 'due_date': row[8]
            })
    except Exception as e:
        print(f"[❌ Cloud Error] Real-time data sync failed: {e}")
    return books_list

def pull_remote_to_local():
    """Pulls sheet mutations downstream to update the offline cache database."""
    if IS_RENDER_CLOUD:
        return False
    try:
        response = urllib.request.urlopen(SHEET_CSV_URL, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if not rows:
            return False

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for row in rows[1:]:
            while len(row) < 9:
                row.append("")
            cursor.execute('''
                INSERT INTO books (id, title, author, category, status, borrowed_by, level_section, date_borrowed, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title, author=excluded.author, category=excluded.category,
                    status=excluded.status, borrowed_by=excluded.borrowed_by, 
                    level_section=excluded.level_section, date_borrowed=excluded.date_borrowed, due_date=excluded.due_date
            ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            
        conn.commit()
        conn.close()
        print("[⚡ Local Sync] Cloud records cached locally successfully.")
        return True
    except Exception as e:
        print(f"[❌ Sync Offline Warning] Offline mode operational: {e}")
        return False

def get_live_books_data():
    """Extracts lightning fast catalog listings via SQLite architecture data trees."""
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

import urllib.request
import csv
import io

# 🔗 VERIFIED CLOUD BACKEND DATABASE DIRECT PIPELINES
REFERENCE_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTru3u7MU1xdpuI2NIHn3f-gPjGALM_97ipCtO_FD-vQhjwb7ZNDQG4q15toLMGbdGA5JLlKNOE-klv/pub?output=csv'

SCHOLASTIC_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSnt8fXWYKBqRAg9tf2NbKc6OLmkGaC4JqAjyjJWLcCrTZ5OUeB1s3y7x_JgBmuE0cqZlMnBkL7CAyG/pub?output=csv'

def process_and_sanitize_row(row):
    """Cleans up rows altered by Google Sheets dropdown formatting and returns exactly 9 fields."""
    while len(row) < 9:
        row.append("")
    return [
        str(row[0]).strip(),  # Lexile Level / ID
        str(row[1]).strip(),  # Title
        str(row[2]).strip(),  # Author
        str(row[3]).strip(),  # Category
        str(row[4]).strip(),  # Status
        str(row[5]).strip(),  # Borrowed By
        str(row[6]).strip(),  # Level & Section
        str(row[7]).strip(),  # Date Borrowed
        str(row[8]).strip()   # Due Date
    ]

def fetch_sheet_by_url(url):
    """Generic engine helper to safely parse a spreadsheet feed by its specific URL."""
    books_list = []
    try:
        response = urllib.request.urlopen(url, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if rows and len(rows) > 1:
            for row in rows[1:]:
                if not row or not row[0].strip():
                    continue
                clean = process_and_sanitize_row(row)
                books_list.append({
                    'id': clean[0], 'title': clean[1], 'author': clean[2],
                    'category': clean[3], 'status': clean[4], 'borrowed_by': clean[5],
                    'level_section': clean[6], 'date_borrowed': clean[7], 'due_date': clean[8]
                })
    except Exception as e:
        print(f"[❌ API Error] Failed to fetch data from {url}: {e}")
    return books_list

def get_reference_data():
    """Fetches real-time metrics for the Reference Collection."""
    return fetch_sheet_by_url(REFERENCE_CSV_URL)

def get_scholastic_data():
    """Fetches real-time metrics for the Scholastic Collection."""
    return fetch_sheet_by_url(SCHOLASTIC_CSV_URL)

def get_live_books_data():
    """Combines both collections for the main dashboard global tracking overview."""
    return get_reference_data() + get_scholastic_data()

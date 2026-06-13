import urllib.request
import csv
import io

# Direct Live Cloud Spreadsheet Access URL
SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSnt8fXWYKBgRag9tf2NbKc6OLmkGac4JqAjyjWLcCrT250UEb1s3y7x_JgBmUE0cgZ1MnB_7CAyG/pub?gid=0&single=true&output=csv'

def process_and_sanitize_row(row):
    """Cleans up rows altered by Google Sheets dropdown formatting and returns exactly 9 fields."""
    # Ensure row has at least 9 elements to avoid IndexErrors
    while len(row) < 9:
        row.append("")
    
    # Extract exactly the first 9 canonical data columns
    return [
        str(row[0]).strip(),  # Lexile Level (ID)
        str(row[1]).strip(),  # Title
        str(row[2]).strip(),  # Author
        str(row[3]).strip(),  # Category
        str(row[4]).strip(),  # Status (from dropdown)
        str(row[5]).strip(),  # Borrowed By
        str(row[6]).strip(),  # Level & Section
        str(row[7]).strip(),  # Date Borrowed
        str(row[8]).strip()   # Due Date
    ]

def get_live_books_data():
    """Streams real-time inventory metrics directly from the live published Google Sheet feed."""
    books_list = []
    try:
        # Request fresh data with a 5-second connection timeout
        response = urllib.request.urlopen(SHEET_CSV_URL, timeout=5)
        csv_text = response.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(csv_text))
        rows = list(csv_data)
        
        if not rows or len(rows) <= 1:
            return []

        # Parse every inventory row, omitting the header row
        for row in rows[1:]:
            if not row or not row[0].strip():
                continue  # Safely skip blank spacer rows
                
            clean = process_and_sanitize_row(row)
            books_list.append({
                'id': clean[0], 'title': clean[1], 'author': clean[2],
                'category': clean[3], 'status': clean[4], 'borrowed_by': clean[5],
                'level_section': clean[6], 'date_borrowed': clean[7], 'due_date': clean[8]
            })
    except Exception as e:
        print(f"[❌ Live API Error] Failed to fetch real-time spreadsheet data: {e}")
        
    return books_list

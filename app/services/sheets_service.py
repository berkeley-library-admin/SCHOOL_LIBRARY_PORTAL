import urllib.request
import csv
import io
from collections import Counter

# 🔗 VERIFIED CLOUD BACKEND DATABASE DIRECT PIPELINES
REFERENCE_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTozu3PlNtmY3F-gkfJwh-KCfqJzkX3MvVkmxVw6Sll9W8D8-Yl/pub?output=csv'
SCHOLASTIC_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTcnFdt9M9kBybIkgwTCNGmWbXwB2uClujYjWQLCcrJ2s0wHzEy_EpXBWwXcpZHdhs3jY1w/pub?output=csv'

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
        
        if len(rows) > 1:
            for row in rows[1:]:
                if not row or not row[0].strip():
                    continue
                clean = process_and_sanitize_row(row)
                books_list.append({
                    'id': clean[0],
                    'title': clean[1],
                    'author': clean[2],
                    'category': clean[3],
                    'status': clean[4],
                    'borrowed_by': clean[5],
                    'level_section': clean[6],
                    'date_borrowed': clean[7],
                    'due_date': clean[8]
                })
    except Exception as e:
        print(f"[❌ API Error] Failed to fetch data from URL: {e}")
    return books_list

def calculate_copy_counts(books_list):
    """Helper function to inject total_copies and available_copies counts dynamically into every book."""
    # Count occurrences of each title
    total_counts = Counter(book['title'] for book in books_list)
    available_counts = Counter(book['title'] for book in books_list if book['status'].strip().lower() == 'available')
    
    # Inject values back into the dictionaries
    for book in books_list:
        book['total_copies'] = total_counts[book['title']]
        book['available_copies'] = available_counts[book['title']]
    return books_list

def get_reference_data():
    """Fetches real-time metrics for the Reference Collection."""
    raw_books = fetch_sheet_by_url(REFERENCE_CSV_URL)
    return calculate_copy_counts(raw_books)

def get_scholastic_data():
    """Fetches real-time metrics for the Scholastic Collection."""
    raw_books = fetch_sheet_by_url(SCHOLASTIC_CSV_URL)
    return calculate_copy_counts(raw_books)

def get_live_books_data():
    """Combines both collections for the main dashboard global tracking overview."""
    combined_books = get_reference_data() + get_scholastic_data()
    # Recalculate combined totals across both groups if identical books exist in both
    return calculate_copy_counts(combined_books)

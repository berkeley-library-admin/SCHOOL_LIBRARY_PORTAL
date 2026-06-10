import urllib.request
import csv
import io

# paste your complete public Google Sheet CSV URL between the single quotes below
SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSnt8fXWYKBqRAg9tf2NbKc6OLmkGaC4JqAjyjJWLcCrTZ5OUeB1s3y7x_JgBmuE0cqZlMnBkL7CAyG/pub?gid=0&single=true&output=csv'

def get_live_books_data():
    """Fetches real-time book rows from the published Google Sheet CSV feed."""
    try:
        # 1. Send an HTTP request to the live Google link
        response = urllib.request.urlopen(SHEET_CSV_URL)
        
        # 2. Read the raw bytes data and decode it into text strings
        csv_text = response.read().decode('utf-8')
        
        # 3. Use Python's CSV reader to properly parse columns and handle commas safely
        csv_data = csv.reader(io.StringIO(csv_text))
        
        # Convert to a list of lists
        rows = list(csv_data)
        
        if not rows:
            return []
            
        # Extract headers (Row 1: Book ID, Title, Author, Category, Status)
        headers = rows[0]
        books_list = []
        
        # 4. Map rows into professional dictionary formats for our frontend
        for row in rows[1:]:
            # Pad missing cells dynamically if row is cut short
            while len(row) < len(headers):
                row.append("")
                
            book_dict = {
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'category': row[3],
                'status': row[4],
                'borrowed_by': row[5], # Make sure there is a comma at the end of this line!
                
                # PASTE THESE 3 NEW TRACKING PARAMETERS HERE:
                'level_section': row[6] if len(row) > 6 else '',
                'date_borrowed': row[7] if len(row) > 7 else '',
                'due_date': row[8] if len(row) > 8 else ''
            }
            books_list.append(book_dict)
            
        return books_list

    except Exception as e:
        print(f"Error syncing with Google Sheets: {e}")
        return []

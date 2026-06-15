from flask import Blueprint, render_template, current_app
from app.services.sheets_service import get_reference_data, get_scholastic_data, get_live_books_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Renders the central library overview management panel layout metrics dashboard."""
    all_books = get_live_books_data()
    
    total_stock = len(all_books)
    borrowed_count = sum(1 for b in all_books if str(b.get('status', '')).strip().lower() != 'available' and str(b.get('status', '')).strip() != '')
    available_count = total_stock - borrowed_count
    
    # FIX: Change 'index.html' to 'dashboard.html' if that is what your file is named!
    return render_template('dashboard.html', 
                           total_stock=total_stock, 
                           borrowed_count=borrowed_count, 
                           available_count=available_count)

@main_bp.route('/reference')
def reference_catalog():
    """Renders the real-time grid overview framework ledger tracker for the Reference Collection."""
    books = get_reference_data()
    return render_template('catalog.html', 
                           books=books, 
                           collection_title="Reference Collection")

@main_bp.route('/scholastic')
def scholastic_catalog():
    """Renders the real-time grid overview framework ledger tracker for the Scholastic Collection."""
    books = get_scholastic_data()
    return render_template('catalog.html', 
                           books=books, 
                           collection_title="Scholastic Collection")

@main_bp.route('/borrowed')
def borrowed():
    """Scans both Reference and Scholastic cloud data arrays to isolate active outstanding asset loans."""
    reference_books = get_reference_data()
    scholastic_books = get_scholastic_data()
    
    borrowed_list = []
    
    # 1. Parse operational metrics across the Reference spreadsheet feed entries
    for book in reference_books:
        status_clean = str(book.get('status', '')).strip().lower()
        if status_clean != 'available' and status_clean != '':
            book['collection_source'] = 'Reference Collection'
            borrowed_list.append(book)
            
    # 2. Parse operational metrics across the Scholastic spreadsheet feed entries
    for book in scholastic_books:
        status_clean = str(book.get('status', '')).strip().lower()
        if status_clean != 'available' and status_clean != '':
            book['collection_source'] = 'Scholastic Collection'
            borrowed_list.append(book)
            
    # 3. Stream the unified real-time active transaction array payload out to display
    return render_template('borrowed.html', borrowed_books=borrowed_list)

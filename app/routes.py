from flask import Blueprint, render_template, current_app
from app.services.sheets_service import get_reference_data, get_scholastic_data, get_live_books_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Renders the central library overview management panel layout metrics dashboard with all required context."""
    all_books = get_live_books_data()
    
    # Calculate live global operational data stats metrics counters
    total_stock = len(all_books)
    borrowed_count = sum(1 for b in all_books if str(b.get('status', '')).strip().lower() != 'available' and str(b.get('status', '')).strip() != '')
    available_count = total_stock - borrowed_count
    
    # Pack variables into the exact dictionary object framework dashboard.html expects
    stats_payload = {
        'total': total_stock,
        'borrowed': borrowed_count,
        'available': available_count
    }
    
    # Pass BOTH stats and books variables safely over to satisfy the template loops
    return render_template('dashboard.html', stats=stats_payload, books=all_books)

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
    @main_bp.route('/shelves')
def shelf_monitor():
    """Aggregates book titles to monitor total stock versus what is physically on the shelves."""
    all_books = get_live_books_data()
    
    # Dictionary to store tracking metrics for each unique title
    inventory = {}
    
    for book in all_books:
        title = book.get('title', '').strip()
        if not title:
            continue
            
        status = str(book.get('status', '')).strip().lower()
        is_borrowed = status != 'available' and status != ''
        
        # If we haven't seen this book title yet, initialize its metrics
        if title not in inventory:
            inventory[title] = {
                'title': title,
                'author': book.get('author', 'Unknown'),
                'call_number': book.get('call_number', 'N/A'),
                'total_owned': 0,
                'borrowed': 0
            }
            
        # Accumulate copy counts
        inventory[title]['total_owned'] += 1
        if is_borrowed:
            inventory[title]['borrowed'] += 1

    # Calculate final on-shelf numbers for each unique book layout
    shelf_list = []
    for title, data in inventory.items():
        data['on_shelf'] = data['total_owned'] - data['borrowed']
        shelf_list.append(data)
        
    # Sort alphabetically by book title
    shelf_list.sort(key=lambda x: x['title'])
    
    return render_template('shelves.html', inventory=shelf_list)

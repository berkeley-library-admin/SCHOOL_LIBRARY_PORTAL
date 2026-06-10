from flask import Blueprint, render_template, jsonify
from app.services.sheets_service import get_live_books_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    # 1. Fetch live books from our Google Sheet service wrapper
    books = get_live_books_data()
    
    # 2. Compute live library statistics programmatically
    total_books = len(books)
    available_books = sum(1 for b in books if b.get('status', '').strip().lower() == 'available')
    borrowed_books = sum(1 for b in books if b.get('status', '').strip().lower() == 'borrowed')
    
    # 3. Compile statistics metrics dictionary object
    stats = {
        'total': total_books,
        'available': available_books,
        'borrowed': borrowed_books
    }
    
    # 4. Pass down data and calculations to our landing template dashboard
    return render_template('dashboard.html', books=books, stats=stats)

@main_bp.route('/catalog')
def catalog():
    # Pull fresh data from our Google Sheet link wrapper
    books = get_live_books_data()
    return render_template('catalog.html', books=books)
    
@main_bp.route('/borrowed')
def borrowed_panel():
    # Fetch fresh spreadsheet streams
    all_books = get_live_books_data()
    # Filter the array in Python to isolate ONLY borrowed logs
    active_loans = [b for b in all_books if b.get('status', '').strip().lower() == 'borrowed']
    return render_template('borrowed.html', loans=active_loans)
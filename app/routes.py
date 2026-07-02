from flask import Blueprint, render_template, current_app, request, session, redirect, url_for
from app.services.sheets_service import get_reference_data, get_scholastic_data, get_live_books_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/admin-login')
def admin_login():
    """Hidden gateway to activate administrator privilege controls."""
    session['is_admin'] = True
    # Redirects you back to the home dashboard with your admin badge active
    return redirect(url_for('main.index'))

@main_bp.route('/admin-logout')
def admin_logout():
    """Removes administrator status and returns to read-only student mode."""
    session.pop('is_admin', None)
    return redirect(url_for('main.index'))

@main_bp.route('/')
def index():
    """Renders the central library overview dashboard."""
    all_books = get_live_books_data()
    
    total_stock = len(all_books)
    borrowed_count = sum(1 for b in all_books if str(b.get('status', '')).strip().lower() != 'available' and str(b.get('status', '')).strip() != '')
    available_count = total_stock - borrowed_count
    
    stats_payload = {
        'total': total_stock,
        'borrowed': borrowed_count,
        'available': available_count
    }
    
    # Check session memory badge
    is_admin = session.get('is_admin', False)
    return render_template('dashboard.html', stats=stats_payload, books=all_books, is_admin=is_admin)

@main_bp.route('/reference')
def reference_catalog():
    """Renders the Reference Collection."""
    books = get_reference_data()
    is_admin = session.get('is_admin', False)
    return render_template('catalog.html', books=books, collection_title="Reference Collection", is_admin=is_admin)

@main_bp.route('/scholastic')
def scholastic_catalog():
    """Renders the Scholastic Collection."""
    books = get_scholastic_data()
    is_admin = session.get('is_admin', False)
    return render_template('catalog.html', books=books, collection_title="Scholastic Collection", is_admin=is_admin)

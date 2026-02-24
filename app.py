#!/usr/bin/env python3
"""
Inventory Tracking App - Flask Web Version with User Authentication
Multi-user, multi-business platform with PostgreSQL backend
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import re
import uuid

# Load environment variables
load_dotenv()

# Import models
from models import db, User, BusinessAccount, InventoryItem, Expense, IncomeEntry, Shrinkage, Transaction

# Import OCR capability
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
    'sqlite:///inventory.db')  # Fallback for development
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-this')
app.config['JSON_SORT_KEYS'] = False

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize database and login manager
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_active_business():
    """Get the current user's active business"""
    if not current_user.is_authenticated:
        return None
    
    business_id = session.get('business_id')
    if business_id:
        business = BusinessAccount.query.filter_by(
            id=business_id, 
            user_id=current_user.id
        ).first()
        if business:
            return business
    
    # Fallback to first active business
    business = BusinessAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()
    
    if business:
        session['business_id'] = business.id
    return business


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not all([email, username, password, confirm_password]):
            return jsonify({'success': False, 'error': 'All fields required'}), 400
        
        if password != confirm_password:
            return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
        
        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already taken'}), 400
        
        # Create new user
        user = User(email=email, username=username)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('setup_business')})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 400
    
    return render_template('signup.html')


@app.route('/setup-business', methods=['GET', 'POST'])
@login_required
def setup_business():
    """Setup initial business account"""
    if request.method == 'POST':
        data = request.json
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        
        if not business_name or not business_type:
            return jsonify({'success': False, 'error': 'Business name and type required'}), 400
        
        # Create business account
        business = BusinessAccount(
            user_id=current_user.id,
            business_name=business_name,
            business_type=business_type,
            is_active=True
        )
        
        try:
            db.session.add(business)
            db.session.commit()
            session['business_id'] = business.id
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('setup_business.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# MAIN DASHBOARD AND UI ROUTES
# ============================================================================

@app.route('/')
def index():
    """Redirect to dashboard or login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    business = get_user_active_business()
    if not business:
        return redirect(url_for('setup_business'))
    
    return render_template('dashboard.html', business=business)

# ============================================================================
# API ROUTES - ITEMS
# ============================================================================

@app.route('/api/items', methods=['GET'])
@login_required
def get_items():
    """Get all items for current business"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    items = InventoryItem.query.filter_by(business_id=business.id).all()
    
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'sku': item.sku,
        'category': item.category,
        'quantity': item.quantity,
        'unit_cost': item.unit_cost,
        'selling_price': item.selling_price,
        'on_display': item.on_display
    } for item in items])


@app.route('/api/items', methods=['POST'])
@login_required
def add_item():
    """Add new item"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    data = request.json
    try:
        item = InventoryItem(
            id=str(uuid.uuid4()),
            business_id=business.id,
            name=data['name'],
            sku=data.get('sku'),
            category=data.get('category'),
            quantity=int(data.get('quantity', 0)),
            unit_cost=float(data.get('unit_cost', 0)),
            selling_price=float(data.get('selling_price', 0))
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'success': True, 'item_id': item.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/items/<item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """Get specific item"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    item = InventoryItem.query.filter_by(id=item_id, business_id=business.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify({
        'id': item.id,
        'name': item.name,
        'sku': item.sku,
        'category': item.category,
        'quantity': item.quantity,
        'unit_cost': item.unit_cost,
        'selling_price': item.selling_price,
        'on_display': item.on_display
    })


@app.route('/api/items/<item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    item = InventoryItem.query.filter_by(id=item_id, business_id=business.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/items/<item_id>/quantity', methods=['POST'])
@login_required
def update_item_quantity(item_id):
    """Update item quantity"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    item = InventoryItem.query.filter_by(id=item_id, business_id=business.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.json
    try:
        quantity_change = int(data.get('change', 0))
        transaction_type = data.get('type', 'adjustment')
        
        item.quantity += quantity_change
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            item_id=item.id,
            transaction_type=transaction_type,
            quantity=quantity_change
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - EXPENSES
# ============================================================================

@app.route('/api/expenses', methods=['GET'])
@login_required
def get_expenses():
    """Get all expenses"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    limit = request.args.get('limit', default=50, type=int)
    expenses = Expense.query.filter_by(business_id=business.id).order_by(
        Expense.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': expense.id,
        'description': expense.description,
        'category': expense.category,
        'amount': expense.amount,
        'item_id': expense.item_id,
        'created_at': expense.created_at.isoformat()
    } for expense in expenses])


@app.route('/api/expenses', methods=['POST'])
@login_required
def add_expense():
    """Add new expense"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    data = request.json
    try:
        expense = Expense(
            id=str(uuid.uuid4()),
            business_id=business.id,
            description=data['description'],
            amount=float(data['amount']),
            category=data.get('category'),
            item_id=data.get('item_id')
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({'success': True, 'expense_id': expense.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    """Delete an expense"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    expense = Expense.query.filter_by(id=expense_id, business_id=business.id).first()
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - INCOME (Snack Bar & Retail)
# ============================================================================

@app.route('/api/income', methods=['GET'])
@login_required
def get_income():
    """Get all income entries"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    limit = request.args.get('limit', default=50, type=int)
    income = IncomeEntry.query.filter_by(business_id=business.id).order_by(
        IncomeEntry.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': entry.id,
        'description': entry.description,
        'category': entry.category,
        'amount': entry.amount,
        'quantity': entry.quantity,
        'created_at': entry.created_at.isoformat()
    } for entry in income])


@app.route('/api/income', methods=['POST'])
@login_required
def add_income():
    """Add income entry"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    data = request.json
    try:
        entry = IncomeEntry(
            id=str(uuid.uuid4()),
            business_id=business.id,
            description=data['description'],
            amount=float(data['amount']),
            category=data.get('category', 'sales'),
            quantity=data.get('quantity')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({'success': True, 'income_id': entry.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API ROUTES - SHRINKAGE
# ============================================================================

@app.route('/api/shrinkage', methods=['POST'])
@login_required
def add_shrinkage():
    """Record shrinkage/loss"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    data = request.json
    try:
        item_id = data['item_id']
        quantity = int(data['quantity'])
        reason = data.get('reason', 'unknown')
        
        item = InventoryItem.query.filter_by(
            id=item_id, 
            business_id=business.id
        ).first()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        value = item.selling_price * quantity
        
        shrinkage = Shrinkage(
            id=str(uuid.uuid4()),
            business_id=business.id,
            item_id=item_id,
            quantity=quantity,
            reason=reason,
            value=value
        )
        
        db.session.add(shrinkage)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/shrinkage', methods=['GET'])
@login_required
def get_shrinkage_report():
    """Get shrinkage report"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    shrinkage = Shrinkage.query.filter_by(business_id=business.id).all()
    
    return jsonify([{
        'item_id': s.item_id,
        'item_name': s.item.name if s.item else 'Unknown',
        'quantity_lost': s.quantity,
        'total_value': s.value,
        'reason': s.reason,
        'created_at': s.created_at.isoformat()
    } for s in shrinkage])


# ============================================================================
# API ROUTES - STATISTICS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get business statistics"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    items = InventoryItem.query.filter_by(business_id=business.id).all()
    expenses = Expense.query.filter_by(business_id=business.id).all()
    income = IncomeEntry.query.filter_by(business_id=business.id).all()
    shrinkage = Shrinkage.query.filter_by(business_id=business.id).all()
    
    total_items = len(items)
    total_quantity = sum(item.quantity for item in items)
    total_inventory_value = sum(item.quantity * item.selling_price for item in items)
    total_expenses = sum(expense.amount for expense in expenses)
    total_income = sum(entry.amount for entry in income)
    total_shrinkage_value = sum(s.value for s in shrinkage)
    
    profit = total_income - total_expenses - total_shrinkage_value
    
    return jsonify({
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_inventory_value': round(total_inventory_value, 2),
        'total_expenses': round(total_expenses, 2),
        'total_income': round(total_income, 2),
        'total_shrinkage': round(total_shrinkage_value, 2),
        'profit': round(profit, 2),
        'business_type': business.business_type
    })


# ============================================================================
# OCR AND RECEIPT PROCESSING
# ============================================================================

def parse_receipt(text):
    """Parse receipt text to extract items and prices"""
    items = []
    lines = text.strip().split('\n')
    
    price_pattern = r'(\$?[\d,]+\.?\d{0,2})'
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 2:
            continue
        
        prices = re.findall(price_pattern, line)
        
        if prices:
            item_name = re.sub(price_pattern, '', line).strip()
            price_str = prices[-1]
            
            price_str = price_str.replace('$', '').replace(',', '').strip()
            
            try:
                price = float(price_str)
                
                if price > 0.01 and item_name:
                    items.append({
                        'name': item_name,
                        'price': price,
                        'quantity': 1
                    })
            except ValueError:
                pass
    
    seen = set()
    unique_items = []
    for item in items:
        key = (item['name'].lower(), item['price'])
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    return unique_items


@app.route('/api/receipt/process', methods=['POST'])
@login_required
def process_receipt():
    """Process receipt image with OCR"""
    if not HAS_OCR:
        return jsonify({'success': False, 'error': 'OCR not available'}), 400
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        image = Image.open(filepath)
        text = pytesseract.image_to_string(image)
        
        os.remove(filepath)
        
        items = parse_receipt(text)
        
        return jsonify({
            'success': True,
            'items': items,
            'raw_text': text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/inventory/bulk-add', methods=['POST'])
@login_required
def bulk_add_items():
    """Add multiple items from receipt"""
    business = get_user_active_business()
    if not business:
        return jsonify({'error': 'No active business'}), 400
    
    data = request.json
    items = data.get('items', [])
    
    if not items:
        return jsonify({'success': False, 'error': 'No items provided'}), 400
    
    try:
        added_items = []
        for item in items:
            new_item = InventoryItem(
                id=str(uuid.uuid4()),
                business_id=business.id,
                name=item['name'],
                category='Receipt Import',
                unit_cost=float(item.get('price', 0)),
                selling_price=float(item.get('price', 0)),
                quantity=int(item.get('quantity', 1))
            )
            db.session.add(new_item)
            added_items.append(new_item.id)
        
        db.session.commit()
        return jsonify({'success': True, 'added_count': len(added_items)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500


# ============================================================================
# CLI COMMANDS FOR DATABASE SETUP
# ============================================================================

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

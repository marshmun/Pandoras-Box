# Inventory Tracker - Multi-User Edition

A production-grade web application for managing inventory, expenses, and business operations across multiple business types (Snack Bar, Retail, Service-based).

## Features

✅ **User Authentication** - Secure login/signup with bcrypt password hashing
✅ **Multi-Business Support** - Manage multiple businesses as one user
✅ **Business Type Differentiation** - Customized features per business type
✅ **Inventory Management** - Add/edit/delete items with cost and selling price tracking
✅ **Expense Tracking** - Record all business expenses
✅ **Income Tracking** - Track sales and revenue (Snack Bar & Retail)
✅ **Receipt OCR** - Scan receipts to auto-import items
✅ **Shrinkage Tracking** - Record losses and damage
✅ **Real-time Stats** - Dashboard with profit calculations
✅ **Dark Mode** - Eye-friendly interface with localStorage persistence
✅ **Responsive Design** - Mobile-optimized interface
✅ **PostgreSQL Backend** - Production-ready database

## System Requirements

- Python 3.8+
- PostgreSQL 12+ (or SQLite for development)
- Tesseract OCR (optional, for receipt scanning)

## Installation

### 1. Setup PostgreSQL Database

**Windows:**
```bash
# Download and install PostgreSQL from https://www.postgresql.org/download/windows/
# During installation, remember the password you set for the postgres user

# After installation, open PowerShell and create a database:
psql -U postgres
# Enter your password when prompted

# In psql, run:
CREATE DATABASE inventory_app;
\q
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
psql postgres
CREATE DATABASE inventory_app;
\q
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

sudo -u postgres psql
CREATE DATABASE inventory_app;
\q
```

### 2. Clone/Download Project

```bash
cd inventory
```

### 3. Create Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/inventory_app

# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-generate-a-strong-random-string
DEBUG=True
```

Replace `your_password` with the PostgreSQL password you set during installation.

### 6. Initialize Database

```bash
# Create database tables
flask init-db

# Or run:
python app.py
```

When the app starts, it will automatically create all tables if they don't exist.

### 7. (Optional) Install Tesseract for OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. In your terminal: `set PATH=%PATH%;C:\Program Files\Tesseract-OCR`

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu):**
```bash
sudo apt-get install tesseract-ocr
```

### 8. Run Application

```bash
python app.py
```

Server will be available at: `http://localhost:5000`

Access from other devices on your network:
- Get your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Navigate to: `http://YOUR_IP:5000`

## Usage

### First Time Setup

1. **Create Account**
   - Go to `/signup`
   - Enter email, username, and password (min 8 characters)
   - Click "Create Account"

2. **Setup Business**
   - Select business type:
     - **Snack Bar**: Inventory + Sales tracking
     - **Retail**: Stock management + Profit analysis
     - **Service**: Hours + Mileage tracking
     - **Other**: Custom tracking
   - Enter business name
   - Click "Continue"

### Dashboard Features

#### Inventory Tab
- **Add Items**: Click "+ Add Item" and enter item details
- **Edit Items**: Click "Edit" on item cards (coming soon)
- **Delete Items**: Click "Delete" to remove items
- **Track Quantity**: Update stock levels in real-time

#### Expenses Tab  
- **Record Expenses**: Click "+ Add Expense"
- **Categories**: Organize by type (Rent, Supplies, etc.)
- **Delete**: Remove expense entries

#### Income Tab (Snack Bar & Retail)
- **Record Sales**: Click "+ Add Income"
- **Track Quantity**: Record units sold
- **Revenue Analysis**: View total income in stats

#### Receipt Scanner Tab
- **Upload Images**: Drag and drop or click to upload receipt photos
- **Auto-Extract**: OCR automatically finds items and prices
- **Bulk Import**: Add all extracted items to inventory

#### Reports Tab
- **Profit Analysis**: Income - Expenses - Shrinkage
- **Inventory Value**: Current stock value
- **Shrinkage Tracking**: View losses and damage records

## Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (String) - Unique email address
- `username` (String) - Unique username  
- `password_hash` (String) - Bcrypt hashed password
- `created_at`, `updated_at` - Timestamps

### Business Accounts Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to Users
- `business_name` (String) - User-defined business name
- `business_type` (String) - 'snack_bar', 'retail', 'service', 'other'
- `is_active` (Boolean) - Active flag

### Inventory Items Table
- `id` (UUID) - Primary key
- `business_id` (UUID) - Foreign key to BusinessAccount
- `name` (String) - Item name
- `sku` (String) - Stock keeping unit
- `category` (String) - Item category
- `quantity` (Integer) - Current stock
- `unit_cost` (Float) - Cost per unit
- `selling_price` (Float) - Price per unit
- `on_display` (Integer) - Units on display

### And more...
- **Transactions** - Stock and adjustments history
- **Expenses** - Business expenses
- **Income** - Sales and revenue entries
- **Shrinkage** - Loss and damage records
- **Mileage Posts** - Mileage tracking (Service)
- **Time Entries** - Hours tracking (Service)

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - Register new user
- `POST /setup-business` - Create business account
- `GET /logout` - User logout

### Inventory
- `GET /api/items` - Get all items
- `POST /api/items` - Add new item
- `GET /api/items/<id>` - Get specific item
- `DELETE /api/items/<id>` - Delete item
- `POST /api/items/<id>/quantity` - Update quantity

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add expense
- `DELETE /api/expenses/<id>` - Delete expense

### Income
- `GET /api/income` - Get all income entries
- `POST /api/income` - Add income

### Other
- `POST /api/shrinkage` - Record shrinkage
- `GET /api/stats` - Get statistics
- `POST /api/receipt/process` - Process receipt OCR

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "localhost" to address
```
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct in .env

### Port 5000 Already in Use
```bash
# Find and kill process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Mac/Linux
```

### OCR Not Working
Ensure Tesseract is installed and properly set in PATH

### User Can't Login
- Verify email/password are correct
- Check PostgreSQL is running
- Review app logs for errors

## Development

### Project Structure
```
inventory/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy ORM models
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (create this)
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── setup_business.html
│   └── dashboard.html
├── static/
│   ├── app.js
│   └── style.css
└── uploads/              # Temporary receipt images
```

### Adding New Features

To add a new feature:
1. Define model in `models.py`
2. Create database migration: `flask db migrate`
3. Add API routes in `app.py`
4. Update frontend in `templates/` and `static/`
5. Test thoroughly

## Deployment

For production deployment:

1. **Use a proper WSGI server** (Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

2. **Set production environment:**
   ```
   FLASK_ENV=production
   DEBUG=False
   FLASK_SECRET_KEY=<generate-strong-secret>
   ```

3. **Use a reverse proxy** (Nginx)

4. **Enable HTTPS** (Let's Encrypt)

5. **Regular backups** of PostgreSQL database

## Support

For issues or questions, check the logs:
```bash
# Flask development server shows all logs in console
# For production, configure logging to file
```

## License

Private project - All rights reserved

## Version History

- **v2.0** - Auth system, PostgreSQL, multi-business support
- **v1.0** - Initial Flask web version

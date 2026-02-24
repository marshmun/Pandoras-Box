# Inventory & Expense Tracking App

A mobile-friendly application to track inventory items, expenses, display items, and shrinkage using Python and Flask.

## Features

- **Inventory Management**
  - Add and track inventory items
  - Track quantities and SKUs
  - Monitor items on display
  - Record unit costs and selling prices

- **Expense Tracking**
  - Log all business expenses
  - Categorize expenses
  - Delete expenses with one click
  - Linked expense tracking to inventory items

- **Receipt Scanner** 📸 (OCR-powered)
  - Upload photos of receipts
  - Automatically extract items and prices
  - Batch add items to inventory
  - Requires: Tesseract OCR (see setup below)

- **Shrinkage & Loss Tracking**
  - Record damaged or lost items
  - Track shrinkage by reason
  - Calculate monetary impact of losses

- **Profit Tracking** 💰
  - Real-time profit calculation
  - Formula: (Inventory Value) - Expenses - Shrinkage
  - Visual profit indicator

- **Reports**
  - View shrinkage reports
  - Monitor expense trends
  - Inventory value calculations
  - Dark mode support

## Setup

### Prerequisites
- Python 3.8+
- Flask
- Tesseract OCR (for Receipt Scanner feature)

### Installation

1. **Clone/Download the project**
   ```bash
   cd inventory
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Tesseract OCR (for Receipt Scanner):**
   
   **Windows (Recommended):**
   - Download installer: https://github.com/UB-Mannheim/tesseract/wiki
   - Or use Chocolatey: `choco install tesseract`
   - Default path: `C:\Program Files\Tesseract-OCR`
   
   **Mac:**
   ```bash
   brew install tesseract
   ```
   
   **Linux:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```
   
   The app will be available at: `http://localhost:5000`

## Using From Your iPhone

1. Open Safari on iPhone
2. Go to: `http://<YOUR_PC_IP>:5000`
3. (Optional) Tap Share → Add to Home Screen for app-like experience

Find your PC's IP address:
```bash
ipconfig  # On Windows
```
Look for IPv4 Address (usually 192.168.x.x)

## Project Structure

```
inventory/
├── app.py                   # Flask application & API
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html          # Web interface
├── static/
│   ├── style.css          # Styling (with dark mode)
│   └── app.js             # Frontend logic
├── src/
│   └── models/
│       └── database.py    # SQLite database layer
├── uploads/               # Receipt images (temporary)
└── README.md             # This file
```

## Usage

### Adding Items
1. Go to **Inventory** tab
2. Click **+ Add Item**
3. Enter details and save

### Recording Expenses
1. Go to **Expenses** tab
2. Click **+ Add Expense**
3. Enter amount and category

### Using Receipt Scanner
1. Go to **Receipt** tab
2. Click **📷 Take/Upload Receipt**
3. Upload a receipt photo
4. Review extracted items
5. Click items to select/deselect
6. Click **Add Selected Items**

### Recording Shrinkage/Loss
1. Go to **Inventory** tab
2. Click an item
3. Click **Record Loss**
4. Enter quantity and reason

### Viewing Reports
1. Go to **Reports** tab
2. View shrinkage summary with impacts

## Features Detail

### Dark Mode
Click the moon icon (🌙) in the header to toggle between light and dark modes. Settings are saved.

### Profit Calculation
Profit = (Current Inventory Value) - (Total Expenses) - (Shrinkage Value)
- Shows in green when positive
- Shows in red when negative

### Receipt OCR
Requires Tesseract OCR to be installed. The app will:
1. Read the receipt image
2. Extract all item names and prices
3. Show items for review
4. Create new inventory items with costs

If Tesseract is not installed, you'll see a helpful error message.

## Troubleshooting

### Receipt Scanner Not Working
- Make sure Tesseract OCR is installed
- Check that it's in your system PATH
- Try restarting the Flask server

### Can't Connect From iPhone
- Ensure both devices are on same WiFi network
- Check firewall settings on PC
- Verify the IP address is correct

### Database Issues
- Delete `inventory.db` to start fresh
- The database will auto-create on startup

## Future Enhancements

- Export reports to CSV/PDF
- Multi-location support
- Barcode scanning
- Item photos
- Cloud sync
- Mobile app deployment

## License

Personal use project


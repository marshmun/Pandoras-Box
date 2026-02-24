# Quick Start: Receipt Scanner Setup

## Your Receipt Scanner is Built! 📸

The Receipt OCR feature is now fully integrated into your app. You just need to install **Tesseract OCR** to activate it.

### Install Tesseract on Windows (Easy Way)

**Option 1: Using Chocolatey (Fastest)**
```powershell
# In PowerShell as Administrator:
choco install tesseract
```

**Option 2: Manual Download**
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: `tesseract-ocr-w64-setup-v5.x.exe`
3. Run installer (accept all defaults)
4. Installation path will be: `C:\Program Files\Tesseract-OCR`

**Option 3: Without Installation**
If you can't install system-wide, modify `app.py` to point to local Tesseract:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\path\to\tesseract.exe'
```

### Once Installed

1. Restart your Flask server
2. Open app on your iPhone: `http://192.168.1.185:5000`
3. Go to **Receipt** tab
4. Click **📷 Take/Upload Receipt**
5. Upload a receipt photo
6. Review extracted items
7. Click items to select/deselect
8. Click **Add Selected Items**

### How It Works

1. **Photo Upload** → Tesseract OCR reads the image
2. **Text Extraction** → Parses item names and prices
3. **Smart Matching** → Suggests existing items or creates new ones
4. **Batch Add** → Adds all selected items to inventory instantly

### What It Can Read

✅ Supermarket receipts  
✅ Restaurant bills  
✅ Store invoices  
✅ Handwritten prices (varies by quality)  
✅ Multi-language text  

### Troubleshooting

**"Tesseract not found" error?**
- Make sure Tesseract is installed
- Restart Flask server after installation
- Check it's in your PATH (PowerShell: `tesseract --version`)

**Receipt items not parsed?**
- Use clear, well-lit photos
- Make sure text is readable
- Try different receipt angles

**Missing items from extraction?**
- OCR accuracy depends on photo quality
- You can always manually add items too

---

**Your app already has everything else ready!**

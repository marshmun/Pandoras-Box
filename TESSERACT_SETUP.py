#!/usr/bin/env python3
"""
Tesseract OCR Setup Instructions

For Windows:
This script provides setup instructions for Tesseract OCR
"""

TESSERACT_SETUP_INSTRUCTIONS = """
===== SETTING UP TESSERACT OCR =====

The Receipt Scanner feature requires Tesseract OCR to read receipts.

----- FOR WINDOWS -----

Option 1: Using PowerShell (Recommended)
1. Open PowerShell as Administrator
2. Run: choco install tesseract
   (Requires Chocolatey - if not installed, first run in PowerShell:
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')))
3. Restart Python/Flask server after installation

Option 2: Manual Installation
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: tesseract-ocr-w64-setup-v5.x.exe
3. Run the installer
4. When prompted for installation path, note it (usually C:\\Program Files\\Tesseract-OCR)
5. Add to your Python app by modifying app.py before creating Flask app:
   
   import pytesseract
   pytesseract.pytesseract.pytesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
   
6. Restart Flask server

----- FOR MAC -----
brew install tesseract

----- FOR LINUX -----
sudo apt-get install tesseract-ocr

Once installed, you'll be able to:
- Upload receipt photos
- Automatically extract item names and prices
- Add items to inventory in one click
"""

if __name__ == '__main__':
    print(TESSERACT_SETUP_INSTRUCTIONS)

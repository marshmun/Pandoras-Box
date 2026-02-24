# Inventory Tracking App - Development Guide

This is a Python Kivy mobile app for tracking inventory, expenses, and shrinkage.

## Project Overview

- **Language:** Python 3.8+
- **Framework:** Kivy (cross-platform UI)
- **Database:** SQLite
- **Target:** Desktop & Mobile (iOS/Android via Buildozer)

## Key Components

### Database Layer (src/models/database.py)
- SQLite database initialization
- Item management operations
- Expense tracking
- Shrinkage recording
- Report generation

### UI Application (src/main.py)
- Tabbed interface (Inventory, Expenses, Reports)
- Item management dialogs
- Expense entry
- Real-time updates

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run app: `python src/main.py`
3. Add items, record expenses, track shrinkage

## Development Tasks

When working on this project, consider:
- Adding more detailed inventory reports
- Implementing search/filter functionality
- Adding data export capabilities
- Optimizing UI for mobile screens
- Implementing item photos/documentation
- Adding multi-location support

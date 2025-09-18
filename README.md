# Inventory Management System (Flask)

A simple, modern inventory management web application built with Flask and SQLAlchemy. It helps you manage products, locations, and track product movements (stock-in, stock-out, transfers). Includes a dashboard, balance report, and a JSON API for balance export.

## Features
- Products: Create, list, edit, delete with quantity tracking
- Locations: Create, list, edit, delete
- Movements: Record stock-in, stock-out, and transfer operations
- Dashboard: Summary stats and recent movements
- Balance report: Current stock by product and location
- Flash messages and basic validation
- JSON API: `/api/balance` to export stock balance

## Tech Stack
- Python 3.x
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- SQLite (file: `inventory.db`)
- Vanilla HTML/CSS templates (Jinja2), custom stylesheet under `static/css/style.css`

## Project Structure
```
Inventry_app/
├─ app.py                 # Flask app with routes and initialization
├─ models.py              # SQLAlchemy models: Product, Location, ProductMovement
├─ requirements.txt       # Python dependencies
├─ test_report.py         # Utility test for balance/report generation (console)
├─ instance/
│  └─ inventory.db        # Created on first run (SQLite database)
├─ template/              # Jinja2 templates (HTML UI)
│  ├─ base.html
│  ├─ dashboard.html
│  ├─ product.html (legacy single-page, see products/*)
│  ├─ movement.html (legacy single-page, see movements/*)
│  ├─ location.html (legacy single-page, see locations/*)
│  ├─ products/
│  │  ├─ list.html
│  │  └─ form.html
│  ├─ locations/
│  │  ├─ list.html
│  │  └─ form.html
│  ├─ movements/
│  │  ├─ list.html
│  │  └─ form.html
│  └─ report.html
└─ static/
   └─ css/
      └─ style.css
```

## Getting Started

### 1) Create and activate a virtual environment (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Run the app
```powershell
python app.py
```
The app will start at http://127.0.0.1:5000

On first run, the SQLite database `inventory.db` is created automatically and tables are initialized.

## Usage Overview
- Dashboard: `/` or `/dashboard`
- Products: `/products` (Add: `/products/add`, Edit: `/products/<product_id>/edit`)
- Locations: `/locations` (Add: `/locations/add`, Edit: `/locations/<location_id>/edit`)
- Movements: `/movements` (Add: `/movements/add`, Edit: `/movements/<movement_id>/edit`)
- Balance Report: `/report`

Stock logic:
- Stock In: leave "From Location" empty and choose a "To Location".
- Stock Out: choose a "From Location" and leave "To Location" empty.
- Transfer: set both "From Location" and "To Location".

## API
Currently, the app exposes a balance API for integrations.

- GET `/api/balance`
  - Returns a JSON array of non-zero balances per product per location.
  - Example response item:
    ```json
    {
      "product_id": "LAP123",
      "product_name": "Laptop",
      "location_id": "WH1",
      "location_name": "Main Warehouse",
      "quantity": 12
    }
    ```

## Running the balance test (optional)
`test_report.py` prints helpful diagnostics to the console.
```powershell
python test_report.py
```

## Configuration
- Database URI: configured in `app.py` as `sqlite:///inventory.db`
- Secret Key: set in `app.py` for flash sessions; replace `your-secret-key-here` for production.

## Notes
- This README describes the current Flask+Jinja application UI. If you plan to migrate the UI to React later, you will need to add CORS and additional REST endpoints.
- All data is stored locally in `inventory.db`. For production, consider PostgreSQL/MySQL and proper configuration management.

## License
MIT (or your preferred license)

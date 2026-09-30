# Advanced Expense Tracker

A strong portfolio-ready expense management application built with Python, Streamlit, SQLite and Pandas.

## Features
- Dashboard with total, monthly and average spending
- Expense CRUD with search, category and date filters
- SQLite persistent database
- Budget planner with usage and remaining budget
- Recurring expense management
- Category, monthly, merchant and payment analytics
- CSV export
- Responsive Streamlit UI
- No external database setup required

## Project Structure
```text
Advanced Expense Tracker/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── expenses.db       # generated automatically
└── src/
    ├── database.py
    ├── analytics.py
    └── utils.py
```

## Run on Windows PowerShell
```powershell
cd "Advanced Expense Tracker"
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Then open:
`http://localhost:8501`

## Run without virtual environment
```powershell
cd "Advanced Expense Tracker"
pip install -r requirements.txt
streamlit run app.py
```

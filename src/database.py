import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, amount REAL NOT NULL, category TEXT NOT NULL,
        payment_method TEXT, merchant TEXT, note TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS budgets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL,
        UNIQUE(month, category)
    );
    CREATE TABLE IF NOT EXISTS recurring(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, amount REAL NOT NULL, frequency TEXT NOT NULL,
        category TEXT NOT NULL, next_due TEXT NOT NULL, active INTEGER DEFAULT 1
    );
    """)
    c.commit(); c.close()

def add_expense(date, amount, category, payment_method, merchant, note):
    c=conn(); c.execute("INSERT INTO expenses(date,amount,category,payment_method,merchant,note) VALUES(?,?,?,?,?,?)",
                        (date,amount,category,payment_method,merchant,note)); c.commit(); c.close()

def get_expenses():
    c=conn()
    df=pd.read_sql_query("SELECT id,date,amount,category,payment_method,merchant,note FROM expenses ORDER BY date DESC,id DESC", c)
    c.close(); return df

def delete_expense(id):
    c=conn(); c.execute("DELETE FROM expenses WHERE id=?", (id,)); c.commit(); c.close()

def add_budget(month, category, amount):
    c=conn(); c.execute("""INSERT INTO budgets(month,category,amount) VALUES(?,?,?)
                           ON CONFLICT(month,category) DO UPDATE SET amount=excluded.amount""",(month,category,amount))
    c.commit(); c.close()

def get_budgets():
    c=conn(); rows=[dict(r) for r in c.execute("SELECT * FROM budgets ORDER BY month DESC,category")]; c.close(); return rows

def delete_budget(id):
    c=conn(); c.execute("DELETE FROM budgets WHERE id=?", (id,)); c.commit(); c.close()

def add_recurring(name, amount, frequency, category, next_due, active):
    c=conn(); c.execute("INSERT INTO recurring(name,amount,frequency,category,next_due,active) VALUES(?,?,?,?,?,?)",
                        (name,amount,frequency,category,next_due,int(active))); c.commit(); c.close()

def get_recurring():
    c=conn(); rows=[dict(r) for r in c.execute("SELECT * FROM recurring ORDER BY next_due")]; c.close(); return rows

def delete_recurring(id):
    c=conn(); c.execute("DELETE FROM recurring WHERE id=?", (id,)); c.commit(); c.close()

def update_recurring(id, active):
    c=conn(); c.execute("UPDATE recurring SET active=? WHERE id=?", (int(active),id)); c.commit(); c.close()

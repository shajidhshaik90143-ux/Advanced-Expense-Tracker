import streamlit as st
import pandas as pd
from datetime import date, datetime
from src.database import init_db, add_expense, get_expenses, delete_expense, add_budget, get_budgets, delete_budget, add_recurring, get_recurring, delete_recurring, update_recurring
from src.analytics import summary_metrics, category_summary, monthly_summary, budget_status
from src.utils import export_csv

st.set_page_config(page_title="Advanced Expense Tracker", page_icon="💰", layout="wide")
init_db()

st.markdown("""
<style>
.main-title {font-size: 2.3rem;font-weight:800;margin-bottom:0}
.subtitle {color:#64748b;margin-bottom:1.5rem}
.card {padding:18px;border-radius:16px;background:linear-gradient(135deg,#f8fafc,#eef2ff);border:1px solid #e2e8f0}
.metric-label{color:#64748b;font-size:.85rem}.metric-value{font-size:1.65rem;font-weight:800}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Advanced Expense Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Track spending, budgets, recurring bills and financial trends in one place.</div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Expense", "Expenses", "Budgets", "Recurring", "Analytics", "Export"])
st.sidebar.divider()
st.sidebar.caption("SQLite • Pandas • Plotly • Streamlit")

df = get_expenses()
metrics = summary_metrics(df)

if menu == "Dashboard":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Spent", f"₹{metrics['total']:,.2f}")
    c2.metric("This Month", f"₹{metrics['month']:,.2f}")
    c3.metric("Transactions", metrics["count"])
    c4.metric("Average Expense", f"₹{metrics['average']:,.2f}")
    st.divider()
    left,right = st.columns(2)
    with left:
        st.subheader("Spending by Category")
        cat = category_summary(df)
        if not cat.empty:
            st.bar_chart(cat.set_index("category")["amount"])
        else:
            st.info("No expenses yet.")
    with right:
        st.subheader("Monthly Spending")
        mon = monthly_summary(df)
        if not mon.empty:
            st.line_chart(mon.set_index("month")["amount"])
        else:
            st.info("Add expenses to see trends.")
    st.subheader("Recent Transactions")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

elif menu == "Add Expense":
    st.subheader("➕ Add Expense")
    with st.form("expense_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1: expense_date = st.date_input("Date", date.today())
        with c2: amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)
        with c3: category = st.selectbox("Category", ["Food","Transport","Shopping","Bills","Entertainment","Health","Education","Travel","Rent","Subscriptions","Other"])
        c1,c2 = st.columns(2)
        with c1: payment = st.selectbox("Payment Method", ["Cash","UPI","Credit Card","Debit Card","Bank Transfer","Other"])
        with c2: merchant = st.text_input("Merchant / Payee", placeholder="e.g. Amazon")
        note = st.text_area("Notes", placeholder="Optional details")
        submitted = st.form_submit_button("Save Expense", type="primary")
        if submitted:
            add_expense(str(expense_date), amount, category, payment, merchant, note)
            st.success("Expense added successfully.")
            st.rerun()

elif menu == "Expenses":
    st.subheader("📋 Expense Manager")
    if df.empty:
        st.info("No expenses recorded.")
    else:
        c1,c2,c3 = st.columns(3)
        search = c1.text_input("Search", placeholder="Merchant, note, category...")
        cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
        selected = c2.selectbox("Category", cats)
        date_range = c3.date_input("Date range", value=(date.today().replace(day=1), date.today()))
        view = df.copy()
        if search:
            mask = view.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            view = view[mask]
        if selected != "All": view = view[view["category"] == selected]
        if isinstance(date_range, tuple) and len(date_range) == 2:
            view["date_dt"] = pd.to_datetime(view["date"])
            view = view[(view["date_dt"].dt.date >= date_range[0]) & (view["date_dt"].dt.date <= date_range[1])].drop(columns=["date_dt"])
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.caption(f"{len(view)} transaction(s) shown.")
        if not view.empty:
            del_id = st.number_input("Transaction ID to delete", min_value=0, step=1, value=0)
            if st.button("Delete Transaction") and del_id:
                delete_expense(int(del_id)); st.success("Deleted."); st.rerun()

elif menu == "Budgets":
    st.subheader("🎯 Budget Planner")
    with st.form("budget_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        month = c1.date_input("Month", date.today().replace(day=1))
        category = c2.selectbox("Category", ["Overall","Food","Transport","Shopping","Bills","Entertainment","Health","Education","Travel","Rent","Subscriptions","Other"])
        amount = c3.number_input("Budget (₹)", min_value=1.0, step=500.0)
        if st.form_submit_button("Set Budget", type="primary"):
            add_budget(month.strftime("%Y-%m"), category, amount)
            st.success("Budget saved."); st.rerun()
    budgets = get_budgets()
    if budgets:
        bdf = pd.DataFrame(budgets)
        st.dataframe(bdf, use_container_width=True, hide_index=True)
        status = budget_status(df, bdf)
        st.subheader("Budget Status")
        st.dataframe(status, use_container_width=True, hide_index=True)
        bid = st.number_input("Budget ID to delete", min_value=0, step=1, value=0)
        if st.button("Delete Budget") and bid:
            delete_budget(int(bid)); st.rerun()
    else: st.info("No budgets configured.")

elif menu == "Recurring":
    st.subheader("🔁 Recurring Expenses")
    with st.form("recurring_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        name = c1.text_input("Name", placeholder="Netflix / Rent / Internet")
        amount = c2.number_input("Amount (₹)", min_value=0.01, step=100.0)
        frequency = c3.selectbox("Frequency", ["Monthly","Weekly","Yearly"])
        c1,c2,c3 = st.columns(3)
        category = c1.selectbox("Category", ["Bills","Subscriptions","Rent","Education","Health","Other"])
        next_due = c2.date_input("Next Due", date.today())
        active = c3.checkbox("Active", value=True)
        if st.form_submit_button("Add Recurring Expense", type="primary"):
            add_recurring(name, amount, frequency, category, str(next_due), active)
            st.success("Recurring expense added."); st.rerun()
    rdf = get_recurring()
    if rdf:
        st.dataframe(pd.DataFrame(rdf), use_container_width=True, hide_index=True)
        rid = st.number_input("Recurring ID", min_value=0, step=1, value=0)
        c1,c2 = st.columns(2)
        if c1.button("Toggle Active") and rid:
            item = next((x for x in rdf if x["id"] == rid), None)
            if item: update_recurring(rid, not bool(item["active"]))
            st.rerun()
        if c2.button("Delete Recurring") and rid:
            delete_recurring(int(rid)); st.rerun()
    else: st.info("No recurring expenses.")

elif menu == "Analytics":
    st.subheader("📊 Financial Analytics")
    if df.empty:
        st.info("Add transactions first.")
    else:
        cat = category_summary(df)
        mon = monthly_summary(df)
        c1,c2 = st.columns(2)
        with c1:
            st.write("Category Breakdown")
            st.bar_chart(cat.set_index("category"))
        with c2:
            st.write("Monthly Trend")
            st.line_chart(mon.set_index("month"))
        st.subheader("Top Merchants")
        merchant = df.groupby("merchant", dropna=False)["amount"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(merchant)
        st.subheader("Payment Method Distribution")
        pay = df.groupby("payment_method")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(pay)

elif menu == "Export":
    st.subheader("📤 Export Data")
    st.write("Download your expense records as CSV.")
    csv = export_csv(df)
    st.download_button("Download Expenses CSV", csv, "expenses.csv", "text/csv")
    st.write(f"Records available: **{len(df)}**")

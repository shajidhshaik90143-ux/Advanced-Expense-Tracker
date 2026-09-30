from datetime import date
import pandas as pd

def summary_metrics(df):
    if df.empty: return {"total":0,"month":0,"count":0,"average":0}
    dates=pd.to_datetime(df["date"])
    this_month=date.today().strftime("%Y-%m")
    return {"total":float(df["amount"].sum()),
            "month":float(df.loc[dates.dt.strftime("%Y-%m")==this_month,"amount"].sum()),
            "count":int(len(df)),
            "average":float(df["amount"].mean())}

def category_summary(df):
    if df.empty: return pd.DataFrame(columns=["category","amount"])
    return df.groupby("category",as_index=False)["amount"].sum().sort_values("amount",ascending=False)

def monthly_summary(df):
    if df.empty: return pd.DataFrame(columns=["month","amount"])
    x=df.copy(); x["month"]=pd.to_datetime(x["date"]).dt.strftime("%Y-%m")
    return x.groupby("month",as_index=False)["amount"].sum().sort_values("month")

def budget_status(df,budgets):
    if budgets.empty: return budgets
    out=budgets.copy()
    if df.empty:
        out["spent"]=0.0
    else:
        x=df.copy(); x["month"]=pd.to_datetime(x["date"]).dt.strftime("%Y-%m")
        vals=[]
        for _,r in out.iterrows():
            if r["category"]=="Overall":
                v=x.loc[x["month"]==r["month"],"amount"].sum()
            else:
                v=x.loc[(x["month"]==r["month"])&(x["category"]==r["category"]),"amount"].sum()
            vals.append(v)
        out["spent"]=vals
    out["remaining"]=out["amount"]-out["spent"]
    out["usage_%"]=(out["spent"]/out["amount"]*100).round(1)
    out["status"]=out.apply(lambda r:"Over Budget" if r["spent"]>r["amount"] else ("Near Limit" if r["spent"]>=r["amount"]*.8 else "On Track"),axis=1)
    return out

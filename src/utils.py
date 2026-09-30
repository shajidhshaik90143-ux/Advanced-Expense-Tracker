import pandas as pd
def export_csv(df):
    return df.to_csv(index=False).encode("utf-8")

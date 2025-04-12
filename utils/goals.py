# utils/goals.py

def suggest_savings_goal(df):
    total = df["Amount"].sum()
    if total < 5000:
        return 500
    elif total < 15000:
        return 2000
    else:
        return round(0.2 * total)
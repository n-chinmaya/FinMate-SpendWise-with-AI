def suggest_savings_goal(df):
    total = df["Amount"].sum()
    # 30% of total expenses as savings suggestion
    return round(0.3 * total)

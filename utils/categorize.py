def categorize_expenses(df):
    def simple_rule(merchant):
        merchant = merchant.lower()
        if "swiggy" in merchant or "zomato" in merchant:
            return "Food"
        elif "amazon" in merchant:
            return "Shopping"
        elif "uber" in merchant or "ola" in merchant:
            return "Transport"
        else:
            return "Others"
    
    df["Category"] = df["Merchant"].apply(simple_rule)
    return df

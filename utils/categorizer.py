# utils/categorizer.py

def categorize(df):
    def simple_rule(merchant):
        merchant = merchant.lower()
        if "swiggy" in merchant or "zomato" in merchant:
            return "Food"
        elif "amazon" in merchant or "flipkart" in merchant:
            return "Shopping"
        elif "uber" in merchant or "ola" in merchant:
            return "Transport"
        elif "bescom" in merchant or "electricity" in merchant or "water" in merchant:
            return "Utilities"
        elif "rent" in merchant or "housing" in merchant:
            return "Housing"
        elif "bigbasket" in merchant or "groceries" in merchant:
            return "Groceries"
        elif "netflix" in merchant or "prime" in merchant:
            return "Entertainment"
        else:
            return "Others"

    df["Category"] = df["Merchant"].apply(simple_rule)
    return df

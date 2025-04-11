import streamlit as st
import pandas as pd
from utils.categorize import categorize_expenses
from utils.goals import suggest_savings_goal

st.set_page_config(page_title="FinMate", layout="centered")
st.title("💸 FinMate - Budgeting App (No AI)")

uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    df = categorize_expenses(df)
    st.subheader("🧠 Categorized Expenses")
    st.dataframe(df)

    savings_goal = suggest_savings_goal(df)
    st.success(f"🎯 Your Recommended Monthly Savings Goal is ₹{savings_goal}")
else:
    st.info("No file uploaded. Showing sample data.")
    df = pd.read_csv("data/sample_transactions.csv")
    st.dataframe(df)

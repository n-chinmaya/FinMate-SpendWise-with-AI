import streamlit as st
import pandas as pd
import plotly.express as px
from utils.categorizer import categorize
from utils.goals import suggest_savings_goal
import os
from datetime import datetime
from utils.ml_model import train_model, predict_future_spending
from utils.emailer import send_email
from utils.pdf_report import PDFReport
from transformers import pipeline

# --- Page Configuration ---
st.set_page_config(page_title="FinMate", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
        .title {text-align: center; color: #2D3E50; font-size: 36px; font-weight: bold;}
        .section-header {color: #2D3E50; font-size: 24px; font-weight: 600;}
        .sidebar-header {font-size: 18px; font-weight: 600;}
        .stButton>button {background-color: #3C82B0; color: white; font-weight: bold; border-radius: 12px;}
        .stButton>button:hover {background-color: #2F66A0;}
        .stAlert {background-color: #E6F7FF;}
    </style>
""", unsafe_allow_html=True)

# --- Login Page ---
def login():
    st.title("🔐 Login to FinMate")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    valid_credentials = {"user1": "password123", "user2": "securepass"}
    if st.button("Login"):
        if username in valid_credentials and valid_credentials[username] == password:
            st.success("✅ Login successful!")
            st.session_state["logged_in"] = True
        else:
            st.error("❌ Invalid username or password.")
    if not st.session_state.get("logged_in", False):
        st.stop()

login()

# --- Main Title ---
st.markdown("<h1 class='title'>💸 FinMate</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #6C757D;'>Your AI-Powered Budgeting Companion</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Upload or Fallback ---
uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File loaded!")
else:
    st.info("Using sample data.")
    df = pd.read_csv("data/sample_transactions.csv")

# --- Categorize ---
df = categorize(df)
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.strftime("%B")

# --- Filters ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🔍 Filters</h2>", unsafe_allow_html=True)
    months = ["All"] + sorted(df["Month"].unique())
    selected_month = st.selectbox("Select Month", months)
    categories = ["All"] + sorted(df["Category"].unique())
    selected_category = st.selectbox("Select Category", categories)

filtered_df = df.copy()
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == selected_month]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# --- Monthly Budget ---
st.sidebar.subheader("📉 Set Monthly Budget")
monthly_budget = st.sidebar.number_input("Set monthly budget (₹)", min_value=1000, step=500, value=10000)

# --- Summary Section ---
if not filtered_df.empty:
    st.subheader("📊 Summary of Your Spending")
    col1, col2, col3 = st.columns(3)
    total_spent = filtered_df["Amount"].sum()
    top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()
    top_category_spent = filtered_df.groupby("Category")["Amount"].sum().max()
    savings_goal = suggest_savings_goal(filtered_df)

    with col1:
        st.metric(label="💰 Total Spending", value=f"₹{total_spent}")
    with col2:
        st.metric(label="🏆 Top Spending Category", value=f"{top_category} (₹{top_category_spent})")
    with col3:
        st.metric(label="💡 Suggested Savings Goal", value=f"₹{savings_goal}")

# --- Calculate Spending Trends ---
filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
current_date = datetime.now()
days_passed = (current_date - filtered_df["Date"].min()).days
total_spent_so_far = filtered_df["Amount"].sum()
avg_daily_spending = total_spent_so_far / days_passed if days_passed > 0 else 0
days_in_month = (filtered_df["Date"].max().replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).day
remaining_days = days_in_month - days_passed
forecasted_spending = total_spent_so_far + (avg_daily_spending * remaining_days)

# --- Achievements Section ---
st.subheader("🏆 Achievements")
badges = []
if total_spent < monthly_budget:
    badges.append("🏅 Budget Master")
    st.success("🎉 Congratulations! You stayed under budget this month! 🏅")
if savings_goal and forecasted_spending < savings_goal:
    badges.append("🥇 Savings Guru")
    st.success("💰 Great job! You are on track to meet your savings goal! 🥇")
if "Entertainment" in filtered_df["Category"].unique():
    entertainment_spending = filtered_df[filtered_df["Category"] == "Entertainment"]["Amount"].sum()
    if entertainment_spending < 500:
        badges.append("🎭 Entertainment Saver")
        st.success("🎭 You earned the 'Entertainment Saver' badge for spending less than ₹500 on entertainment!")
st.markdown("### Your Badges")
st.write(", ".join(badges) if badges else "No badges earned yet. Keep going!")

# --- Progress Tracking ---
st.subheader("📈 Progress Tracking")
savings_progress = min(int((total_spent / savings_goal) * 100), 100)
budget_progress = min(int((total_spent / monthly_budget) * 100), 100)
st.write(f"💡 Progress toward your savings goal: {savings_progress}%")
st.progress(savings_progress)
st.write(f"📉 Progress toward staying under budget: {budget_progress}%")
st.progress(budget_progress)

# --- Daily Challenges ---
st.subheader("🎯 Daily Challenges")
daily_challenge = "Spend less than ₹500 today!"
st.write(f"Today's Challenge: {daily_challenge}")
today = datetime.now().date()
today_spending = filtered_df[filtered_df["Date"] == pd.Timestamp(today)]["Amount"].sum()
if today_spending < 500:
    st.success("🎉 Challenge completed! Great job!")
else:
    st.warning("⚠️ Try again tomorrow!")

# --- Tabs for Navigation ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📌 Insights", "🤖 AI Assistant", "🔮 Predictive Alerts", "📤 Reports"])

# --- Dashboard Tab ---
with tab1:
    st.subheader("📊 Dashboard")
    st.dataframe(filtered_df)
    st.write(f"💸 Total Spending: ₹{total_spent:.2f}")
    st.progress(min(int((total_spent / monthly_budget) * 100), 100))
    
    # Add spending forecast
    try:
        predicted_spending = predict_future_spending(filtered_df)
        st.write(f"🔮 Predicted Spending for Tomorrow: ₹{predicted_spending:.2f}")
    except Exception as e:
        st.error(f"❌ Error predicting future spending: {e}")

# --- Insights Tab ---
with tab2:
    st.subheader("📌 Smart Insights")
    top_cat = filtered_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    if not top_cat.empty:
        st.bar_chart(top_cat)
        fig = px.pie(top_cat, names=top_cat.index, values=top_cat.values, title="💸 Spending Distribution by Category")
        st.plotly_chart(fig)
        
        # Add average spending per category
        avg_spending_per_category = filtered_df.groupby("Category")["Amount"].mean().sort_values(ascending=False)
        st.write("### Average Spending Per Category")
        st.dataframe(avg_spending_per_category)

# --- AI Assistant Tab ---
with tab3:
    st.subheader("🤖 Ask FinMate AI")
    user_query = st.text_input("Ask a question about your spending (e.g., 'What is my top category?')")
    if st.button("Get Insights"):
        if user_query:
            try:
                if "least spent category" in user_query.lower():
                    least_category = filtered_df.groupby("Category")["Amount"].sum().idxmin()
                    least_spent = filtered_df.groupby("Category")["Amount"].sum().min()
                    response = f"The least spent category is '{least_category}' with ₹{least_spent:.2f}."
                elif "most expensive day" in user_query.lower():
                    most_expensive_day = filtered_df.groupby("Date")["Amount"].sum().idxmax()
                    response = f"The most expensive day was {most_expensive_day.strftime('%b %d, %Y')}."
                else:
                    response = "Sorry, I couldn't understand your query. Try asking about categories or spending trends."
                st.success(response)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- Predictive Alerts Tab ---
with tab4:
    st.subheader("🔮 Predictive Alerts")
    st.write(f"📊 Average daily spending: ₹{avg_daily_spending:.2f}")
    st.write(f"📅 Remaining days: {remaining_days} days")
    st.write(f"💸 Forecasted spending by end of month: ₹{forecasted_spending:.2f}")
    if forecasted_spending > monthly_budget:
        st.error(f"🚨 Warning! You are on track to exceed your budget by ₹{forecasted_spending - monthly_budget:.2f}.")
    elif forecasted_spending > (monthly_budget * 0.8):
        st.warning(f"⚠️ You are approaching your budget limit! Forecasted spending is ₹{forecasted_spending:.2f}.")
    else:
        st.success(f"✅ On track! You are predicted to stay within your budget. Forecasted spending: ₹{forecasted_spending:.2f}")

# --- Reports Tab ---
with tab5:
    st.subheader("📤 Export PDF Report")
    if st.button("📑 Generate PDF Report"):
        with st.spinner("Generating your report..."):
            try:
                pdf = PDFReport()
                pdf.add_page()
                pdf.section_title(f"Month: {selected_month}")
                pdf.add_summary(total_spent, monthly_budget, savings_goal)
                cat_data = filtered_df.groupby("Category")["Amount"].sum().to_dict()
                pdf.add_category_breakdown(cat_data)
                filename = f"finmate_report_{selected_month.lower()}.pdf"
                filepath = os.path.join("data", filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                pdf.save(filepath)
                with open(filepath, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name=filename)
            except Exception as e:
                st.error(f"❌ Error generating PDF: {e}")

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #6C757D;">
        <p>Made with ❤️ by <strong>FinMate Team</strong></p>
        <p><a href="https://finmate.com" target="_blank">Visit our website</a> | <a href="mailto:support@finmate.com">Contact Support</a></p>
    </div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.categorizer import categorize
from utils.goals import suggest_savings_goal
import os


st.set_page_config(page_title="FinMate", layout="centered")
st.title("💸 FinMate - AI Budgeting Companion")

# --- Upload or fallback ---
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
    st.header("🔍 Filters")
    months = sorted(df["Month"].unique())
    selected_month = st.selectbox("Select Month", months)
    categories = ["All"] + sorted(df["Category"].unique())
    selected_category = st.selectbox("Select Category", categories)

# --- Apply Filters ---
filtered_df = df[df["Month"] == selected_month]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

st.subheader(f"📄 Transactions for {selected_month} - {selected_category}")
st.dataframe(filtered_df)

# --- Savings Goal ---
savings_goal = suggest_savings_goal(filtered_df)
st.success(f"💡 Suggested Monthly Savings Goal: ₹{savings_goal}")

# --- Monthly Budget ---
st.subheader("📉 Total Budget Tracker")
monthly_budget = st.number_input("Set monthly budget (₹)", min_value=1000, step=500)
total_spent = filtered_df["Amount"].sum()
percent_used = (total_spent / monthly_budget) * 100 if monthly_budget else 0

st.write(f"💸 Spent ₹{total_spent:.2f} / ₹{monthly_budget}")
st.progress(min(int(percent_used), 100))

if percent_used >= 100:
    st.error("🚨 Over budget!")
elif percent_used >= 80:
    st.warning("⚠️ Nearing limit.")
else:
    st.success("✅ Within budget.")

# --- Per Category Budgeting ---
st.subheader("📂 Category Budgets")
cat_budgets = {}
for cat in filtered_df["Category"].unique():
    with st.expander(f"📁 {cat}"):
        cat_total = filtered_df[filtered_df["Category"] == cat]["Amount"].sum()
        limit = st.slider(f"Budget for {cat} (₹)", 0, 10000, step=500, key=f"{cat}_budget")
        cat_budgets[cat] = limit

        st.write(f"Spent: ₹{cat_total:.2f} / ₹{limit}")
        if cat_total > limit:
            st.error("🚨 Over budget!")
        elif cat_total > 0.8 * limit:
            st.warning("⚠️ Close to limit.")
        else:
            st.success("✅ OK")

# --- Key Insights ---
st.subheader("📌 Smart Insights")
top_cat = filtered_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
if not top_cat.empty:
    st.write("🏆 Top Spending Categories")
    st.bar_chart(top_cat)

    max_txn = filtered_df.loc[filtered_df["Amount"].idxmax()]
    st.write(f"💥 Highest spend: ₹{max_txn['Amount']} at {max_txn['Merchant']}")

    top_day = filtered_df.groupby("Date")["Amount"].sum().idxmax()
    st.write(f"📅 Most expensive day: {top_day.strftime('%b %d, %Y')}")

# --- Charts ---
st.subheader("📊 Charts")
col1, col2 = st.columns(2)
with col1:
    pie = px.pie(filtered_df, names="Category", values="Amount", title="Category Split")
    st.plotly_chart(pie, use_container_width=True)

with col2:
    line = px.line(filtered_df.groupby("Date")["Amount"].sum().reset_index(),
                   x="Date", y="Amount", title="Daily Spend")
    st.plotly_chart(line, use_container_width=True)

import os
import streamlit as st
from utils.emailer import send_email
from utils.pdf_report import PDFReport  # Ensure the import path is correct for PDFReport

# --- PDF Export Section ---
st.subheader("📤 Export PDF Report")
filepath = None  # Initialize filepath here

if st.button("📄 Generate PDF Report"):
    try:
        # Initialize PDFReport instance
        pdf = PDFReport()
        pdf.add_page()

        # Adding content to the PDF
        pdf.section_title(f"Month: {selected_month}")
        pdf.add_summary(total_spent, monthly_budget, savings_goal)

        cat_data = filtered_df.groupby("Category")["Amount"].sum().to_dict()
        pdf.section_title("Category Breakdown")
        pdf.add_category_breakdown(cat_data)

        if not filtered_df.empty:
            top_merchant = filtered_df.loc[filtered_df["Amount"].idxmax()]["Merchant"]
            max_amt = filtered_df["Amount"].max()
            pdf.section_title("Top Spend")
            pdf.add_top_spends(top_merchant, max_amt)

        # Setting the file path
        filename = f"finmate_report_{selected_month.lower()}.pdf"
        filepath = os.path.join("data", filename)

        # Ensure the directory exists before saving
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Saving the PDF
        print(f"Saving PDF to: {filepath}")  # Debugging line
        pdf.save(filepath)

        # Check if the file exists and provide the download button
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Download PDF", data=f, file_name=filename, mime="application/pdf")
            st.success("✅ PDF generated successfully!")
        else:
            st.error("❌ Failed to generate PDF. Please try again.")
    except Exception as e:
        st.error(f"❌ Error during PDF generation: {e}")

# --- Email Section ---
st.subheader("📧 Email the Report")
with st.form("email_form"):
    receiver = st.text_input("Your Email")
    sender = st.text_input("Sender Gmail", help="Use a Gmail ID you control")
    password = st.text_input("Sender App Password", type="password", help="Use App Password, not actual Gmail password")
    submit = st.form_submit_button("Send Email")

    if submit:
        if filepath and os.path.exists(filepath):  # Check if file exists
            try:
                send_email(
                    receiver_email=receiver,
                    subject=f"FinMate Report for {selected_month}",
                    body="Attached is your monthly spend summary.",
                    file_path=filepath,
                    sender_email=sender,
                    sender_password=password
                )
                st.success("✅ Email sent successfully!")
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
        else:
            st.error("❌ No PDF generated. Please generate the report first.")
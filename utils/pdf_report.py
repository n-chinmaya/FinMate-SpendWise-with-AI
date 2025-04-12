from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "FinMate Monthly Report", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(4)

    def add_summary(self, total, budget, goal):
        self.set_font("Arial", "", 11)
        self.cell(0, 10, f"Total Spent: Rs. {total}", ln=True)
        self.cell(0, 10, f"Monthly Budget: Rs. {budget}", ln=True)
        self.cell(0, 10, f"Savings Goal: Rs. {goal}", ln=True)
        self.ln(10)

    def add_category_breakdown(self, category_data):
        self.set_font("Arial", "", 10)
        for cat, amt in category_data.items():
            self.cell(0, 8, f"{cat}: Rs. {amt}", ln=True)
        self.ln(10)

    def add_top_spends(self, top_merchant, max_txn):
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Top Spending Merchant: {top_merchant} - Rs. {max_txn}", ln=True)
        self.ln(10)

    def save(self, filename="finmate_report.pdf"):
        self.output(filename)
        return filename

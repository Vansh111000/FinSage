import os
import getpass
import time
import csv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datasets import load_dataset
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# If API key not found, prompt securely
if not API_KEY:
    API_KEY = getpass.getpass("Enter your Google Gemini API key: ")
    os.environ["GOOGLE_API_KEY"] = API_KEY

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# Helper: Generate with retry
# -------------------------------
def generate_with_retry(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except ResourceExhausted as e:
            retry_delay = getattr(e, "retry_delay", None)
            wait_time = retry_delay.seconds if retry_delay else 10
            st.warning(f"Quota exceeded. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    st.error("Max retries reached. Try again later.")
    return None

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="FinSage – AI Financial Coach", page_icon="💸", layout="wide")
st.title("💸 FinSage – AI Financial Coach")
st.caption("Upload your financial CSV file to see category-wise spending and AI insights.")

# -------------------------------
# Initialize AI context (optional)
# -------------------------------
with st.expander("🧠 Initialize AI Knowledge Base (optional)"):
    st.write("Loading reference financial dataset...")
    dataset = load_dataset("Akhil-Theerthala/PersonalFinance-CoTR-5K")
    st.success("AI financial knowledge base loaded successfully!")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload your financial CSV file", type=["csv"])

if uploaded_file is not None:
    # Try to detect delimiter automatically
    sample = uploaded_file.read(2048).decode("utf-8", errors="ignore")
    uploaded_file.seek(0)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","

    try:
        # Read CSV
        user_data = pd.read_csv(uploaded_file, delimiter=delimiter, on_bad_lines="skip", engine="python", header=None)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    # Ensure minimum 4 columns
    if user_data.shape[1] >= 4:
        user_data = user_data.iloc[:, :4]
        user_data.columns = ["date", "amount", "category", "description"]
    else:
        st.error("❌ CSV must contain at least 4 columns: Date, Amount, Category, Description.")
        st.stop()

    # Clean Data
    user_data.columns = [c.strip().lower() for c in user_data.columns]
    user_data["amount"] = pd.to_numeric(user_data["amount"], errors="coerce").fillna(0)
    user_data["category"] = user_data["category"].astype(str).str.strip().replace("", "Uncategorized")

    # Remove rows where the category column is the header itself
    user_data = user_data[user_data['category'].str.lower() != "category"]

    # Filter out income-related rows
    def is_expense(cat):
        c = str(cat).lower()
        if "income" in c or "salary" in c or "earning" in c:
            return False
        return True

    user_data = user_data[user_data["category"].apply(is_expense)]

    if user_data.empty:
        st.info("ℹ️ No expense transactions found in your data.")
        st.stop()

    # Group and summarize
    category_summary = user_data.groupby("category")["amount"].sum().sort_values(ascending=False)

    # Display total expenditure
    total_spent = category_summary.sum()
    st.subheader(f"💵 Total Expenditure: ₹{total_spent:,.2f}")
    st.write("Here’s a breakdown of your spending across categories:")

    # -------------------------------
    # Bar Graph
    # -------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(category_summary.index, category_summary.values, color="#E74C3C")
    ax.set_title("Category-wise Expenditure", fontsize=16, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Total Amount (₹)")
    ax.set_xticklabels(category_summary.index, rotation=45, ha="right")

    # Add labels on top of bars
    ax.bar_label(bars, fmt="₹%.0f", fontsize=9)
    plt.tight_layout()

    # Show the chart
    st.pyplot(fig)

    # Show summary table below
    st.subheader("📊 Summary Table")
    st.dataframe(category_summary.reset_index().rename(columns={"category": "Category", "amount": "Total Spent (₹)"}))
    # -------------------------------
    # AI Insights Section
    # -------------------------------
    st.subheader("🧠 AI Financial Insights")

    total_spent = user_data["amount"].sum()
    avg_spent = user_data["amount"].mean()
    max_spent = user_data["amount"].max()
    top_categories = user_data.groupby("category")["amount"].sum().sort_values(ascending=False).head(3)
    top_cats_text = ", ".join([f"{cat} (₹{amt:,.2f})" for cat, amt in top_categories.items()])
    sample_data = user_data.head(15).to_string(index=False)

    prompt = f"""
You are a professional financial coach and certified investment advisor.
Analyze this user's transaction data and provide a structured, 500-word report.

Include:
1. A concise numerical summary (total, average, highest spending, top 3 categories with ₹ values)
2. Spending patterns or imbalances (where money is spent most)
3. 2–3 recommendations to control expenses or save more
4. Investment recommendations based on potential savings:
   - Low-risk (FDs, PPF, emergency fund)
   - Moderate-risk (SIPs, mutual funds)
   - High-risk (ETFs, equity)
5. Highlight any financial risks or red flags.
6. End with an actionable 3–4 point summary with ₹ values where useful.

User Snapshot:
• Total spent: ₹{total_spent:,.2f}
• Average transaction: ₹{avg_spent:,.2f}
• Highest spend: ₹{max_spent:,.2f}
• Top 3 categories: {top_cats_text}

Sample Transactions:
{sample_data}
"""

    with st.spinner("Generating AI insights..."):
        response = generate_with_retry(prompt)

    if response:
        try:
            ai_output = response.text.strip()
        except AttributeError:
            ai_output = response.candidates[0].content.parts[0].text.strip()
        st.markdown(ai_output)
    else:
        st.error("Failed to generate AI insights. Please try again later.")

else:
    st.info("📂 Upload your financial CSV file to begin analysis.")

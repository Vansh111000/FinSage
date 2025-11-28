import os
import time
import csv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datasets import load_dataset
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
import hashlib

# -----------------------------------
# Helper: Hash passwords
# -----------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------------
# User Database Setup
# -----------------------------------
USER_DB = "users.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_DB, index=False)

def register_user(username, password):
    users = pd.read_csv(USER_DB)
    if username in users["username"].values:
        return False
    new_row = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    users = pd.concat([users, new_row], ignore_index=True)
    users.to_csv(USER_DB, index=False)
    return True

def authenticate(username, password):
    users = pd.read_csv(USER_DB)
    if username in users["username"].values:
        stored_hash = users.loc[users["username"] == username, "password"].values[0]
        return stored_hash == hash_password(password)
    return False

# -----------------------------------
# Load environment variables
# -----------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.warning("⚠️ Missing GOOGLE_API_KEY. Enter manually below:")
    API_KEY = st.text_input("Enter Gemini API Key:", type="password")
    if API_KEY:
        os.environ["GOOGLE_API_KEY"] = API_KEY

# -----------------------------------
# Configure Gemini
# -----------------------------------
model = None
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------------------
# Safe AI Response Handler
# -----------------------------------
def get_safe_response_text(response):
    try:
        return response.text.strip()
    except:
        try:
            return response.candidates[0].content.parts[0].text.strip()
        except:
            return None

# -----------------------------------
# Retry Wrapper
# -----------------------------------
def generate_with_retry(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except ResourceExhausted:
            wait = 10
            st.warning(f"Quota limit hit. Retrying in {wait}s... ({attempt+1}/{max_retries})")
            time.sleep(wait)
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    st.error("Max retry attempts reached.")
    return None

# -----------------------------------
# Streamlit Config
# -----------------------------------
st.set_page_config(page_title="FinSage – AI Financial Coach", page_icon="💸", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------------
# Pages
# -----------------------------------
def home_page():
    st.title("💸 Welcome to FinSage")
    st.write("Your smart AI-powered financial coach.")

    if st.button("🔐 Login"):
        st.session_state.page = "login"
        st.rerun()

    if st.button("🆕 Create Account"):
        st.session_state.page = "signup"
        st.rerun()

def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful!")
            st.session_state.user = username
            st.session_state.page = "dashboard"
            time.sleep(1)
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    if st.button("⬅ Go Back"):
        st.session_state.page = "home"
        st.rerun()

def signup_page():
    st.title("🆕 Create Account")

    username = st.text_input("Create username")
    password = st.text_input("Create password", type="password")
    confirm = st.text_input("Confirm password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.error("Fields cannot be empty.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif register_user(username, password):
            st.success("Account created! Login now.")
            st.session_state.page = "login"
            time.sleep(1)
            st.rerun()
        else:
            st.error("Username already exists.")

    if st.button("⬅ Go Back"):
        st.session_state.page = "home"
        st.rerun()

# def dashboard():
#     st.title(f"📊 Dashboard — Welcome {st.session_state.user}")

#     if st.button("🚪 Logout"):
#         st.session_state.user = None
#         st.session_state.page = "home"
#         st.rerun()

#     uploaded = st.file_uploader("Upload Expense CSV", type=["csv"])

#     if uploaded:
#         sample = uploaded.read(2048).decode("utf-8", errors="ignore")
#         uploaded.seek(0)

#         try:
#             delimiter = csv.Sniffer().sniff(sample).delimiter
#         except:
#             delimiter = ","

#         df = pd.read_csv(uploaded, delimiter=delimiter, header=None)

#         if df.shape[1] < 4:
#             st.error("CSV must contain at least 4 columns.")
#             return

#         df.columns = ["date", "amount", "category", "description"]
#         df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

#         df = df[~df["category"].str.contains("income|salary|deposit", case=False, na=False)]

#         summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
#         total = summary.sum()

#         st.metric("Total Spending", f"₹{total:,.2f}")
#         st.dataframe(summary)

#         fig, ax = plt.subplots()
#         ax.bar(summary.index, summary.values)
#         plt.xticks(rotation=45)
#         st.pyplot(fig)

#         st.subheader("🧠 AI Insights")

#         if st.button("Generate AI Report"):
#             prompt = f"""
# You are a financial advisor. Analyze these expenses:

# Total Spent: ₹{total:,.2f}

# Breakdown:
# {summary.to_string()}

# Return insights, saving tips, and a budget plan.
# """

#             with st.spinner("Generating..."):
#                 response = generate_with_retry(prompt)

#             if not response:
#                 st.error("AI couldn't generate response.")
#                 return
            
#             safe_text = get_safe_response_text(response)

#             if safe_text:
#                 st.markdown(safe_text)
#             else:
#                 st.error("⚠️ AI did not return readable content. Try again.")
def dashboard():
    st.title(f"📊 Dashboard — Welcome {st.session_state.user}")

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    uploaded = st.file_uploader("Upload Expense CSV", type=["csv"])

    if uploaded:
        sample = uploaded.read(2048).decode("utf-8", errors="ignore")
        uploaded.seek(0)

        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
        except:
            delimiter = ","

        df = pd.read_csv(uploaded, delimiter=delimiter, header=None)

        if df.shape[1] < 4:
            st.error("CSV must contain at least 4 columns: date, amount, category, description.")
            return

        df.columns = ["date", "amount", "category", "description"]
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        # 🔥 NEW LOGIC: Detect Income vs Expenses
        income_df = df[df["category"].str.contains("income|salary|deposit|credit", case=False, na=False)]
        expenses_df = df[~df["category"].str.contains("income|salary|deposit|credit", case=False, na=False)]

        total_income = income_df["amount"].sum()
        total_expenses = expenses_df["amount"].sum()
        savings = total_income - total_expenses

        # Show financial metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Income", f"₹{total_income:,.2f}")
        col2.metric("💸 Total Expenses", f"₹{total_expenses:,.2f}")
        col3.metric("📈 Savings", f"₹{savings:,.2f}", delta=savings)

        # Expense Summary
        st.subheader("📂 Expense Breakdown by Category")
        expense_summary = expenses_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.dataframe(expense_summary)

        # 📊 Bar Chart
        fig, ax = plt.subplots()
        ax.bar(expense_summary.index, expense_summary.values)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.divider()

        # 🧠 AI Insights
        st.subheader("🧠 AI Insights")

        if st.button("Generate AI Report"):
            prompt = f"""
Analyze this user's finances and provide a personalized report.

Income: ₹{total_income:,.2f}
Expenses: ₹{total_expenses:,.2f}
Savings: ₹{savings:,.2f}

Expense Breakdown:
{expense_summary.to_string()}

Include:
- Spending habits analysis
- High expense areas
- Recommended monthly budget targets
- Savings and investment suggestions
- Action items to improve financial health
"""

            with st.spinner("Generating..."):
                response = generate_with_retry(prompt)

            safe_text = get_safe_response_text(response)

            if safe_text:
                st.markdown(safe_text)
            else:
                st.error("⚠️ Report could not be generated. Try again.")

# -----------------------------------
# Router
# -----------------------------------
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "dashboard":
    dashboard()

# import os
# import getpass
# import time
# import csv
# import pandas as pd
# import streamlit as st
# import matplotlib.pyplot as plt
# from datasets import load_dataset
# import google.generativeai as genai
# from google.api_core.exceptions import ResourceExhausted
# from dotenv import load_dotenv
# import hashlib

# # -------------------------------
# # Helper: Hash passwords
# # -------------------------------
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # -------------------------------
# # User Database File
# # -------------------------------
# USER_DB = "users.csv"
# if not os.path.exists(USER_DB):
#     pd.DataFrame(columns=["username", "password"]).to_csv(USER_DB, index=False)

# def register_user(username, password):
#     users = pd.read_csv(USER_DB)
#     if username in users["username"].values:
#         return False
#     new_row = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
#     users = pd.concat([users, new_row], ignore_index=True)
#     users.to_csv(USER_DB, index=False)
#     return True

# def authenticate(username, password):
#     users = pd.read_csv(USER_DB)
#     if username in users["username"].values:
#         stored_hash = users.loc[users["username"] == username, "password"].values[0]
#         return stored_hash == hash_password(password)
#     return False

# # -------------------------------
# # Load environment variables
# # -------------------------------
# load_dotenv()

# API_KEY = os.getenv("GOOGLE_API_KEY")

# # Show key debug info (optional)
# # st.write("Loaded API Key:", bool(API_KEY))

# model = None
# try:
#     if not API_KEY:
#         raise ValueError("❌ No API key found. Ensure GOOGLE_API_KEY is set in .env")

#     genai.configure(api_key=API_KEY)
#     model = genai.GenerativeModel("gemini-2.0-flash-exp")  # OR gemini-2.0-flash depending on your key

# except Exception as e:
#     st.error(f"⚠️ Gemini API Configuration Error: {str(e)}")
#     st.info("👉 Get or verify your key here: https://aistudio.google.com/app/apikey")
#     model = None

# # -------------------------------
# # Streamlit Page Configuration
# # -------------------------------
# st.set_page_config(page_title="FinSage – AI Financial Coach", page_icon="💸", layout="wide")

# # Initialize session states
# if "page" not in st.session_state:
#     st.session_state.page = "home"

# if "user" not in st.session_state:
#     st.session_state.user = None

# # -------------------------------
# # Generate AI With Retry
# # -------------------------------
# def generate_with_retry(prompt, max_retries=3):
#     if not model:
#         st.error("AI model not configured. Please check your API key.")
#         return None
        
#     for attempt in range(max_retries):
#         try:
#             response = model.generate_content(prompt)
#             return response
#         except ResourceExhausted as e:
#             wait_time = 10
#             st.warning(f"Quota exceeded. Retrying in {wait_time}s... ({attempt+1}/{max_retries})")
#             time.sleep(wait_time)
#         except Exception as e:
#             st.error(f"API Error: {str(e)}")
#             if "API_KEY_INVALID" in str(e):
#                 st.error("❌ Your API key is invalid. Please verify your key at: https://aistudio.google.com/app/apikey")
#             return None
#     st.error("Max retry limit exceeded.")
#     return None

# # ================================
# # PAGE: HOME
# # ================================
# def home_page():
#     st.title("💸 Welcome to FinSage")
#     st.subheader("Your Personal Smart AI-Powered Financial Coach")
    
#     st.markdown("""
#     ### What FinSage Offers:
#     - 📊 **Spending Analysis**: Upload your transaction data for detailed insights
#     - 🤖 **AI-Powered Guidance**: Get personalized financial recommendations
#     - 📈 **Visual Reports**: See your spending patterns at a glance
#     - 🎯 **Smart Budgeting**: Identify areas to save and optimize
#     """)

#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("🔐 Login", use_container_width=True):
#             st.session_state.page = "login"
#             st.rerun()

#     with col2:
#         if st.button("🆕 Create Account", use_container_width=True):
#             st.session_state.page = "signup"
#             st.rerun()

# # ================================
# # PAGE: LOGIN
# # ================================
# def login_page():
#     st.title("🔐 Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("Login", use_container_width=True):
#             if authenticate(username, password):
#                 st.success("Login Successful! Redirecting...")
#                 st.session_state.user = username
#                 st.session_state.page = "dashboard"
#                 time.sleep(1)
#                 st.rerun()
#             else:
#                 st.error("Invalid username or password.")

#     with col2:
#         if st.button("⬅ Back", use_container_width=True):
#             st.session_state.page = "home"
#             st.rerun()

# # ================================
# # PAGE: SIGNUP
# # ================================
# def signup_page():
#     st.title("🆕 Create Account")

#     username = st.text_input("New Username")
#     password = st.text_input("New Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")

#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("Create Account", use_container_width=True):
#             if not username or not password:
#                 st.error("Please fill in all fields.")
#             elif password != confirm_password:
#                 st.error("Passwords do not match!")
#             elif len(password) < 6:
#                 st.error("Password must be at least 6 characters long.")
#             elif register_user(username, password):
#                 st.success("Account created successfully! You can now login.")
#                 time.sleep(1)
#                 st.session_state.page = "login"
#                 st.rerun()
#             else:
#                 st.error("Username already exists!")

#     with col2:
#         if st.button("⬅ Back", use_container_width=True):
#             st.session_state.page = "home"
#             st.rerun()

# # ================================
# # PAGE: DASHBOARD
# # ================================
# def dashboard():
#     st.title(f"📊 FinSage Dashboard")
#     st.subheader(f"Welcome, {st.session_state.user}!")
    
#     if st.button("🚪 Logout"):
#         st.session_state.user = None
#         st.session_state.page = "home"
#         st.rerun()

#     st.markdown("---")
#     st.caption("📤 Upload your financial CSV file to see category-wise spending and AI insights.")
    
#     uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

#     if uploaded_file:
#         # Detect delimiter
#         sample = uploaded_file.read(2048).decode("utf-8", errors="ignore")
#         uploaded_file.seek(0)
        
#         try:
#             dialect = csv.Sniffer().sniff(sample)
#             delimiter = dialect.delimiter
#         except:
#             delimiter = ","

#         try:
#             df = pd.read_csv(uploaded_file, delimiter=delimiter, on_bad_lines="skip", engine="python", header=None)
#         except Exception as e:
#             st.error(f"Error reading CSV: {e}")
#             return

#         if df.shape[1] < 4:
#             st.error("CSV must contain at least 4 columns: date, amount, category, description")
#             return
        
#         df = df.iloc[:, :4]
#         df.columns = ["date", "amount", "category", "description"]
#         df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

#         # Clean data
#         df = df[~df['category'].str.lower().eq("category")]
#         df = df[~df["category"].str.contains("income|salary|earning", case=False, na=False)]

#         if df.empty:
#             st.info("No expense transactions found in the file.")
#             return

#         # Calculate summary
#         summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
#         total_spent = summary.sum()

#         # Display metrics
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("💰 Total Spending", f"₹{total_spent:,.2f}")
#         with col2:
#             st.metric("📋 Categories", len(summary))
#         with col3:
#             st.metric("🧾 Transactions", len(df))

#         st.markdown("---")

#         # Visualization
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             st.subheader("📊 Category-wise Spending")
#             fig, ax = plt.subplots(figsize=(10, 6))
#             bars = ax.bar(summary.index, summary.values, color='skyblue', edgecolor='navy')
#             ax.set_title("Spending by Category", fontsize=14, fontweight='bold')
#             ax.set_xlabel("Category")
#             ax.set_ylabel("Amount (₹)")
#             ax.bar_label(bars, fmt='₹%.0f')
#             plt.xticks(rotation=45, ha='right')
#             plt.tight_layout()
#             st.pyplot(fig)

#         with col2:
#             st.subheader("📑 Summary Table")
#             summary_df = summary.reset_index()
#             summary_df.columns = ["Category", "Amount"]
#             summary_df["Amount"] = summary_df["Amount"].apply(lambda x: f"₹{x:,.2f}")
#             st.dataframe(summary_df, use_container_width=True)

#         # AI Insights
#         st.markdown("---")
#         st.subheader("🧠 AI Financial Insights")
        
#         if not model:
#             st.warning("⚠️ AI Analysis is not available. Please check your Google Gemini API key configuration.")
#             st.info("Get your API key at: https://aistudio.google.com/app/apikey")
#             return
        
#         if st.button("Generate AI Analysis", type="primary"):
#             prompt = f"""You are a financial advisor. Analyze these expenses and provide:
# 1. Key spending patterns
# 2. Top 3 spending categories analysis
# 3. Practical money-saving suggestions
# 4. Budget optimization tips

# Total Spending: ₹{total_spent:,.2f}

# Category breakdown:
# {summary.to_string()}

# Recent transactions:
# {df.head(15).to_string(index=False)}

# Provide actionable, specific advice in a friendly tone."""

#             with st.spinner("🤔 Analyzing your finances..."):
#                 response = generate_with_retry(prompt)
            
#             if response:
#                 st.markdown(response.text)
#             else:
#                 st.error("Unable to generate insights. Please check your API key and try again.")

# # -------------------------------
# # Page Router
# # -------------------------------
# if st.session_state.page == "home":
#     home_page()
# elif st.session_state.page == "login":
#     login_page()
# elif st.session_state.page == "signup":
#     signup_page()
# elif st.session_state.page == "dashboard":
#     dashboard()
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

# -------------------------------
# Helper: Hash passwords
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# User Database File
# -------------------------------
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


# -------------------------------
# Load Environment Variables
# -------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# -------------------------------
# Configure Gemini (Only Once)
# -------------------------------
if "configured" not in st.session_state:
    if not API_KEY:
        st.error("❌Missing API key. Add GOOGLE_API_KEY to .env")
        st.stop()

    try:
        genai.configure(api_key=API_KEY)
        st.session_state.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        st.session_state.configured = True
    except Exception as e:
        st.error(f"⚠️ Gemini API Configuration Failed: {e}")
        st.stop()


# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="FinSage – AI Financial Coach", page_icon="💸", layout="wide")

# Initialize session states
if "page" not in st.session_state:
    st.session_state.page = "home"

if "user" not in st.session_state:
    st.session_state.user = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# -------------------------------
# AI With Retry + Failure Handling
# -------------------------------
def generate_with_retry(prompt):
    model = st.session_state.model

    try:
        return model.generate_content(prompt)
    except ResourceExhausted:
        st.error("🚨 Quota Exceeded — Try Again Tomorrow or Use a Paid Key.")
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


# ================================ HOME PAGE
def home_page():
    st.title("💸 Welcome to FinSage")
    st.subheader("Your Personal Smart AI-Powered Financial Coach")
    
    st.markdown("""
    ### What FinSage Offers:
    - 📊 Expense Breakdown & Visualization  
    - 🧠 AI-Based Financial Insights  
    - 💡 Personalized Budget Suggestions  
    - 🔐 Secure Login & Profile System  
    """)

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("🆕 Create Account", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()


# ================================ LOGIN PAGE
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True):
            if authenticate(username, password):
                st.success("Login Successful ✔")
                st.session_state.user = username
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password")

    with col2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


# ================================ SIGNUP PAGE
def signup_page():
    st.title("🆕 Create Account")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create Account", use_container_width=True):
            if not username or not password:
                st.error("❌ Please fill all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif register_user(username, password):
                st.success("🎉 Account created successfully!")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Username already exists!")

    with col2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


# ================================ DASHBOARD
def dashboard():
    st.title(f"📊 Dashboard — Welcome {st.session_state.user}")

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    st.markdown("---")
    st.caption("📤 Upload Your Expenses CSV to Generate AI Insights")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        sample = uploaded_file.read(2048).decode("utf-8", errors="ignore")
        uploaded_file.seek(0)

        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
        except:
            delimiter = ","

        df = pd.read_csv(uploaded_file, delimiter=delimiter, header=None)
        df.columns = ["date", "amount", "category", "description"]

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        total_spent = summary.sum()

        st.metric("💰 Total Spending", f"₹{total_spent:,.2f}")
        st.write(summary)

        # ----- AI FINANCIAL INSIGHTS -----
        st.subheader("🧠 AI Financial Advisor")

        if st.button("Generate AI Analysis") and st.session_state.analysis_result is None:
            prompt = f"""
            You are an expert financial advisor analyzing spending patterns.

            Total Spending: ₹{total_spent:,.2f}

            Category Breakdown:
            {summary.to_string()}

            Provide:
            - Spending Patterns
            - Top Category Insights
            - Saving Tips
            - Monthly Budget Plan
            """

            with st.spinner("⏳ Processing AI Insights..."):
                st.session_state.analysis_result = generate_with_retry(prompt)

        if st.session_state.analysis_result:
            st.success("🎉 Analysis Generated!")
            try:
                st.markdown(st.session_state.analysis_result.text)
            except:
                st.markdown(st.session_state.analysis_result.candidates[0].content.parts[0].text)


# -------------------------------
# PAGE ROUTER
# -------------------------------
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "dashboard":
    dashboard()

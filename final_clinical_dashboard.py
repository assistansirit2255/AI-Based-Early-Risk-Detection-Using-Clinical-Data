import streamlit as st
import base64
import time
from modules.cvd_module import run_cvd
from modules.hypertension_module import run_hypertension
from modules.diabetes_module import run_diabetes
from modules.model_comparison import run_model_comparison

st.set_page_config(page_title="AI Clinical System", layout="wide")

# -------------------------
# PASSWORDS (CHANGE HERE)
# -------------------------
DOCTOR_PASSWORD = "admin"
PATIENT_PASSWORD = "1234"

# -------------------------
# BACKGROUND IMAGE
# -------------------------
def set_background():
    with open("ip.jpg", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255,255,255,0.90);
            padding: 2rem;
            border-radius: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# -------------------------
# SESSION STATE
# -------------------------
if "role" not in st.session_state:
    st.session_state.role = None

if "last_active" not in st.session_state:
    st.session_state.last_active = time.time()

# -------------------------



# -------------------------
# LOGIN PAGE
# -------------------------
def login():

    st.title("🔐 AI Multi-Disease Clinical System")

    role = st.selectbox("Login As", ["Patient", "Doctor"])
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):

        if role == "Doctor" and password == DOCTOR_PASSWORD:
            st.session_state.role = "Doctor"
            st.rerun()

        elif role == "Patient" and password == PATIENT_PASSWORD:
            st.session_state.role = "Patient"
            st.rerun()

        else:
            st.error("❌ Incorrect Password")

# -------------------------
# DASHBOARD
# -------------------------
def dashboard():

    role = st.session_state.role

    st.sidebar.title("Navigation")
    st.sidebar.write(f"Logged in as: {role}")

    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.role = None
        st.rerun()

    # Sidebar Navigation
    if role == "Doctor":
        page = st.sidebar.radio(
            "Go to",
            ["Home","Diabetes","Hypertension","Cardiovascular Disease","Model Comparison"]
        )
    else:
        page = st.sidebar.radio(
            "Go to",
            ["Home","Diabetes","Hypertension","Cardiovascular Disease"]
        )

    # -------------------------
    # PAGE ROUTING
    # -------------------------

    if page == "Home":

        st.title("🏥 AI Multi-Disease Clinical Decision Support System")

        st.markdown("### 📌 Project Overview")
        st.write("""
        This AI-driven healthcare system predicts early risk of lifestyle diseases 
        including **Diabetes, Hypertension, and Cardiovascular Disease** using 
        machine learning algorithms.

        The system assists doctors and patients in identifying potential health 
        risks before severe complications occur.
        """)

        st.markdown("### 🎯 Objective")
        st.write("""
        - To support preventive healthcare using Artificial Intelligence  
        - To provide early multi-level risk prediction (Low / Moderate / High)  
        - To improve clinical decision-making through explainable visual analytics  
        """)

        st.markdown("### 🤖 Machine Learning Models Used")
        st.write("""
        - Logistic Regression (Baseline Model)  
        - Support Vector Machine (Comparative Model)  
        - Random Forest (Best Performing Model)  
        """)

        st.markdown("### 📊 Key Features")
        st.write("""
        ✔ Role-based access (Doctor / Patient)  
        ✔ Interactive disease prediction modules  
        ✔ Clinical data visualization for doctors  
        ✔ Risk stratification with lifestyle & diet recommendations  
        ✔ Downloadable AI-generated patient reports  
        ✔ Model comparison analytics  
        """)

        st.markdown("### 🔍 Explainable AI Approach")
        st.write("""
        Unlike traditional black-box prediction systems, this platform 
        provides visual explanations and feature-based insights that 
        help healthcare professionals understand the reasoning behind 
        predictions.
        """)

        st.success("🚀 This system promotes proactive healthcare instead of reactive treatment.")

    elif page == "Diabetes":
        run_diabetes(role)

    elif page == "Hypertension":
        run_hypertension(role)

    elif page == "Cardiovascular Disease":
        run_cvd(role)

    elif page == "Model Comparison":
        run_model_comparison()

# -------------------------
# MAIN
# -------------------------
if st.session_state.role is None:
    login()
else:
    dashboard()
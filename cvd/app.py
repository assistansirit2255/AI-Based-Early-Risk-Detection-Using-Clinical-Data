import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
import base64
# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CVD Risk Dashboard",
    page_icon="🫀",
    layout="wide"
)

def add_bg_from_local(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("OIP.jpg")
# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_cardio_data.csv")

data = load_data()
# --------- BMI CALCULATION ---------
data['bmi'] = data['weight'] / ((data['height'] / 100) ** 2)


# Load ML model
model = joblib.load("cvd_model.pkl")


# ---------------- TITLE ----------------
st.title("🫀 Cardiovascular Disease Risk Prediction Dashboard")
st.markdown(
    "### Research-Based Interactive Dashboard using Machine Learning"
)

# ---------------- KPI SECTION ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Total Patients", len(data))
col2.metric("❤️ CVD Cases", int(data['cardio'].sum()))
col3.metric("📊 Avg Age", round(data['age'].mean(), 1))
col4.metric("⚠️ CVD Rate (%)", round(data['cardio'].mean() * 100, 2))

st.divider()

# ---------------- FILTERS ----------------
st.sidebar.header("🔍 Filter Data")

age_range = st.sidebar.slider(
    "Select Age Range",
    int(data['age'].min()),
    int(data['age'].max()),
    (30, 60)
)

gender_filter = st.sidebar.selectbox(
    "Select Gender",
    ["All", "Male", "Female"]
)

filtered_data = data[
    (data['age'] >= age_range[0]) &
    (data['age'] <= age_range[1])
]
filtered_data = filtered_data.copy()
filtered_data['bmi'] = filtered_data['weight'] / ((filtered_data['height'] / 100) ** 2)


if gender_filter != "All":
    gender_val = 1 if gender_filter == "Male" else 0
    filtered_data = filtered_data[filtered_data['gender'] == gender_val]

# ---------------- VISUALIZATION SECTION ----------------
st.subheader("📊 Risk Factor Analysis")

colA, colB = st.columns(2)

with colA:
    fig_age = px.histogram(
        filtered_data,
        x="age",
        color="cardio",
        title="Age Distribution vs CVD",
        barmode="overlay"
    )
    st.plotly_chart(fig_age, use_container_width=True)

with colB:
    fig_bp = px.box(
        filtered_data,
        x="cardio",
        y="ap_hi",
        title="Systolic BP vs CVD"
    )
    st.plotly_chart(fig_bp, use_container_width=True)

colC, colD = st.columns(2)

with colC:
    fig_chol = px.bar(
        filtered_data.groupby("cholesterol")["cardio"].mean().reset_index(),
        x="cholesterol",
        y="cardio",
        title="Cholesterol Level vs CVD Risk"
    )
    st.plotly_chart(fig_chol, use_container_width=True)

with colD:
    fig_bmi = px.histogram(
        filtered_data,
        x="bmi",
        color="cardio",
        title="BMI Distribution vs CVD"
    )
    st.plotly_chart(fig_bmi, use_container_width=True)

st.divider()

# ---------------- ML MODEL PERFORMANCE ----------------
st.subheader("🤖 Machine Learning Model Overview")

st.markdown("""
**Model Used:** Random Forest / Logistic Regression  
**Features:** Age, Gender, BP, Cholesterol, BMI, Smoking, Alcohol, Physical Activity  
**Target Variable:** Cardiovascular Disease (0 = No, 1 = Yes)
""")

# ---------------- PREDICTION TOOL ----------------
# ---------------- PREDICTION TOOL ----------------
st.subheader("🧪 Individual CVD Risk Prediction Tool")

with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)

    # Column 1
    age = col1.number_input("Age", 18, 100, 45)
    gender = col1.selectbox("Gender", ["Female", "Male"])
    height = col1.number_input("Height (cm)", 100, 220, 165)
    weight = col1.number_input("Weight (kg)", 30, 200, 65)

    # Column 2
    ap_hi = col2.number_input("Systolic BP", 90, 200, 120)
    ap_lo = col2.number_input("Diastolic BP", 60, 140, 80)
    cholesterol = col2.selectbox("Cholesterol Level", [1, 2, 3])

    # Column 3
    gluc = col3.selectbox("Glucose Level", [1, 2, 3])
    smoke = col3.selectbox("Smoking", [0, 1])
    alco = col3.selectbox("Alcohol Intake", [0, 1])
    active = col3.selectbox("Physically Active", [0, 1])

    submit = st.form_submit_button("🔍 Predict Risk")


# -------- Prediction Logic (ONLY ON SUBMIT) --------
# -------- Prediction Logic (ONLY ON SUBMIT) --------
if submit:
    gender_val = 1 if gender == "Male" else 0

    input_data = np.array([[ 
        0,              # id (dummy value)
        age,
        gender_val,
        height,
        weight,
        ap_hi,
        ap_lo,
        cholesterol,
        gluc,
        smoke,
        alco,
        active
    ]])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    if prediction == 1:
        st.error(f"🔴 HIGH RISK of CVD\n\nRisk Probability: {probability:.2%}")
    else:
        st.success(f"🟢 LOW RISK of CVD\n\nRisk Probability: {probability:.2%}")

# ---------------- FOOTER ----------------
st.markdown(
    """
    **Project Title:** AI-Based Early Cardiovascular Disease Risk Prediction  
    **Developed by:** Garima Sharma (BCA – AI & Data Science)  
  
    """
)

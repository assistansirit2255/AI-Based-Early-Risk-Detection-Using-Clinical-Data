import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import os

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Hypertension Risk Dashboard",
    page_icon="🩺",
    layout="wide"
)

# =====================================
# SET BACKGROUND IMAGE
# =====================================
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

if os.path.exists("hp.jpg"):
    set_bg("hp.jpg")

# =====================================
# LOAD MODEL + SCALER + FEATURES
# =====================================
model = joblib.load("hypertension_model.pkl")
scaler = joblib.load("hypertension_scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")

st.title("🩺 Hypertension Risk Prediction System")
st.markdown("AI-Based Clinical Decision Support Tool")
st.markdown("---")

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.header("Patient Clinical Inputs")

age = st.sidebar.slider("Age", 10, 100, 40)
bmi = st.sidebar.slider("BMI", 10.0, 60.0, 28.0)
stress = st.sidebar.slider("Stress Score", 0, 10, 5)
sleep_duration = st.sidebar.slider("Sleep Duration (hrs)", 0, 12, 7)
salt = st.sidebar.slider("Salt Intake Level", 1, 5, 3)

family_history = st.sidebar.selectbox("Family History", ["No", "Yes"])
smoking = st.sidebar.selectbox("Smoking Status", ["Non-Smoker", "Smoker"])
bp_history = st.sidebar.selectbox("BP History", ["Normal", "PreHypertension", "Hypertension"])
exercise = st.sidebar.selectbox("Exercise Level", ["Low", "Moderate", "High"])
medication = st.sidebar.selectbox("Medication", ["None", "Diuretic", "Beta Blocker", "Other"])

# =====================================
# TABS
# =====================================
tab1, tab2 = st.tabs(["🔍 Risk Prediction", "📊 Data Analysis (EDA)"])

# =====================================
# TAB 1 — PREDICTION
# =====================================
with tab1:

    if st.button("🔍 Analyze Hypertension Risk"):

        input_dict = {
            "Age": age,
            "Salt_Intake": salt,
            "Stress_Score": stress,
            "Sleep_Duration": sleep_duration,
            "BMI": bmi
        }

        input_dict["Family_History_Yes"] = 1 if family_history == "Yes" else 0
        input_dict["Smoking_Status_Smoker"] = 1 if smoking == "Smoker" else 0
        input_dict["BP_History_PreHypertension"] = 1 if bp_history == "PreHypertension" else 0
        input_dict["BP_History_Normal"] = 1 if bp_history == "Normal" else 0
        input_dict["Exercise_Level_Moderate"] = 1 if exercise == "Moderate" else 0
        input_dict["Exercise_Level_Low"] = 1 if exercise == "Low" else 0
        input_dict["Medication_Diuretic"] = 1 if medication == "Diuretic" else 0
        input_dict["Medication_Beta Blocker"] = 1 if medication == "Beta Blocker" else 0
        input_dict["Medication_Other"] = 1 if medication == "Other" else 0

        input_df = pd.DataFrame([input_dict])

        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[feature_columns]

        input_scaled = scaler.transform(input_df)
        prob = model.predict_proba(input_scaled)[0][1]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            title={'text': "Risk Probability (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "red" if prob > 0.6 else "orange" if prob > 0.3 else "green"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 100], 'color': "salmon"}
                ],
            }
        ))

        st.plotly_chart(fig)

        if prob < 0.3:
            st.success("✅ LOW RISK — Maintain healthy lifestyle.")
        elif prob < 0.6:
            st.warning("⚠ MEDIUM RISK — Monitor blood pressure regularly.")
        else:
            st.error("🚨 HIGH RISK — Consult a healthcare professional.")

# =====================================
# TAB 2 — EDA
# =====================================
with tab2:

    if os.path.exists("hypertension_dataset.xlsx"):
        data = pd.read_excel("hypertension_dataset.xlsx")
    elif os.path.exists("hypertension_dataset.csv"):
        data = pd.read_csv("hypertension_dataset.csv")
    else:
        st.error("Dataset file not found.")
        st.stop()

    st.write("Dataset Shape:", data.shape)

    st.subheader("Class Distribution")
    fig1, ax1 = plt.subplots()
    sns.countplot(x="Has_Hypertension", data=data, ax=ax1)
    st.pyplot(fig1)

    st.subheader("Correlation Heatmap")
    data_encoded = pd.get_dummies(data, drop_first=True)
    fig2, ax2 = plt.subplots(figsize=(8,6))
    sns.heatmap(data_encoded.corr(), cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)

    st.subheader("Age Distribution")
    fig3, ax3 = plt.subplots()
    sns.histplot(data["Age"], kde=True, ax=ax3)
    st.pyplot(fig3)

    st.subheader("BMI Distribution")
    fig4, ax4 = plt.subplots()
    sns.histplot(data["BMI"], kde=True, ax=ax4)
    st.pyplot(fig4)

st.markdown("---")
st.caption("Developed by Garima Sharma | AI Clinical Intelligence System")

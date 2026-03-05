import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px
import base64
# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Health Risk Prediction",
    page_icon="💉" ,
    layout="centered"
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

@st.cache_data
def load_data():
    return pd.read_csv("diabetes.csv")

data = load_data()

# -----------------------------
# Load & Train Model (Demo)
# -----------------------------
data = pd.read_csv("diabetes.csv")

X = data.drop("Outcome", axis=1)
y = data["Outcome"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# -----------------------------
# TITLE SECTION
# -----------------------------
st.markdown(
    """
    <h1 style='text-align:left ; color: #2C3E50;'>
    🧬Early Diabetes Risk Prediction 
    </h1>
    <h3 style='text-align: center; color: gray;'>
    Patient & Doctor Decision Support System
    </h3>
    <hr>
    """,
    unsafe_allow_html=True
)

st.subheader("📊 Dataset Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric("👥 Total Patients", len(data))
k2.metric("⚠️ Diabetes Cases", int(data["Outcome"].sum()))
k3.metric("📊 Diabetes Rate (%)", round(data["Outcome"].mean() * 100, 2))
k4.metric("🧪 Avg Glucose", round(data["Glucose"].mean(), 1))

st.sidebar.header("🔍 Filter Data")

age_range = st.sidebar.slider(
    "Select Age Range",
    int(data["Age"].min()),
    int(data["Age"].max()),
    (20, 60)
)

outcome_filter = st.sidebar.selectbox(
    "Select Outcome",
    ["All", "Diabetic", "Non-Diabetic"]
)

filtered_data = data[
    (data["Age"] >= age_range[0]) &
    (data["Age"] <= age_range[1])
]

if outcome_filter == "Diabetic":
    filtered_data = filtered_data[filtered_data["Outcome"] == 1]
elif outcome_filter == "Non-Diabetic":
    filtered_data = filtered_data[filtered_data["Outcome"] == 0]
st.divider()
st.subheader("📈 Exploratory Data Analysis")

c1, c2 = st.columns(2)

with c1:
    fig_glucose = px.histogram(
        filtered_data,
        x="Glucose",
        color="Outcome",
        barmode="overlay",
        title="Glucose vs Diabetes"
    )
    st.plotly_chart(fig_glucose, use_container_width=True)

with c2:
    fig_bmi = px.histogram(
        filtered_data,
        x="BMI",
        color="Outcome",
        barmode="overlay",
        title="BMI vs Diabetes"
    )
    st.plotly_chart(fig_bmi, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    fig_age = px.box(
        filtered_data,
        x="Outcome",
        y="Age",
        title="Age vs Diabetes Outcome"
    )
    st.plotly_chart(fig_age, use_container_width=True)

with c4:
    corr = filtered_data.drop("Outcome", axis=1).corr()
    fig_corr = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
    st.plotly_chart(fig_corr, use_container_width=True)

st.divider()
st.subheader("🤖 Machine Learning Model Overview")

st.markdown("""
**Model Used:** Random Forest Classifier  

**Features Used:**  
- Pregnancies  
- Glucose  
- Blood Pressure  
- Skin Thickness  
- Insulin  
- BMI  
- Diabetes Pedigree Function  
- Age  

**Target Variable:**  
- **Diabetes Outcome**  
  - `0` → Non-Diabetic  
  - `1` → Diabetic
""")

# -----------------------------
# PATIENT INPUT FORM
# -----------------------------
st.subheader("🧑‍⚕️ Patient Clinical Details")

col1, col2 = st.columns(2)

with col1:
    pregnancies = st.number_input("Pregnancies", 0, 20, 1)
    glucose = st.number_input("Glucose Level (mg/dL)", 50, 300, 120)
    bp = st.number_input("Blood Pressure (mmHg)", 40, 150, 70)
    skin = st.number_input("Skin Thickness (mm)", 5, 100, 25)

with col2:
    insulin = st.number_input("Insulin Level", 10, 900, 120)
    bmi = st.number_input("BMI", 10.0, 60.0, 32.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5)
    age = st.number_input("Age", 10, 100, 30)

# -----------------------------
# PREDICTION BUTTON
# -----------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔍 Check Diabetes Risk"):
    input_data = np.array([[pregnancies, glucose, bp, skin,
                             insulin, bmi, dpf, age]])

    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)[0][1]

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("📊 Risk Prediction Result")

    # -----------------------------
    # VISUAL RISK INDICATOR
    # -----------------------------
    if prediction[0] == 1:
        st.error("⚠️ HIGH RISK OF DIABETES")
        st.progress(int(probability * 100))
        st.write(f"🔴 Risk Level: **{probability*100:.1f}%**")
        st.warning("Consult a doctor for further medical evaluation.")
    else:
        st.success("✅ LOW RISK OF DIABETES")
        st.progress(int(probability * 100))
        st.write(f"🟢 Risk Level: **{probability*100:.1f}%**")
        st.info("Maintain a healthy lifestyle and regular checkups.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color: gray;'>
    AI-Based Clinical Decision Support System | Academic Project
    </p>
    """,
    unsafe_allow_html=True
)

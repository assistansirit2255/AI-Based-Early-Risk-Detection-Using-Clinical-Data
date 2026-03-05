import streamlit as st
import pandas as pd
import joblib
import os
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from modules.report_generator import generate_report

BASE = os.path.dirname(os.path.dirname(__file__))

def run_diabetes(role):

    st.header("🩸 Diabetes Risk Prediction")

    model = joblib.load(os.path.join(BASE,"diabetes","diabetes_model.pkl"))

    name = st.text_input("Patient Name")

    pregnancies = st.number_input("Pregnancies",0,20,1)
    glucose = st.number_input("Glucose",50,300,120)
    bp = st.number_input("Blood Pressure",40,200,80)
    bmi = st.number_input("BMI",10.0,60.0,25.0)
    age = st.number_input("Age",1,100,30)

    if st.button("Predict Risk"):

        input_data = pd.DataFrame(
            [[pregnancies,glucose,bp,0,0,bmi,0,age]],
            columns=[
                'Pregnancies','Glucose','BloodPressure',
                'SkinThickness','Insulin',
                'BMI','DiabetesPedigreeFunction','Age'
            ]
        )

        prob = model.predict_proba(input_data)[0][1]
        risk = round(prob*100,2)

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk,
            title={'text':"Risk Level (%)"},
            gauge={'axis':{'range':[0,100]}}
        ))
        st.plotly_chart(fig,use_container_width=True)

        # Risk stratification
        if prob < 0.3:
            level="Low Risk"
            diet="High fiber diet, fruits, vegetables."
            lifestyle="30 mins exercise daily."
        elif prob < 0.6:
            level="Moderate Risk"
            diet="Reduce sugar & refined carbs."
            lifestyle="Weight management required."
        else:
            level="High Risk"
            diet="Strict low-carb diet."
            lifestyle="Immediate medical consultation advised."

        st.success(f"Risk Level: {level}")
        st.info(f"Diet: {diet}")
        st.warning(f"Lifestyle: {lifestyle}")

        # 🔵 Doctor Section
        if role == "Doctor":

            st.subheader("📊 Clinical Analytics")

            data = pd.read_csv(
                os.path.join(BASE,"Diabetes","diabetes.csv")
            )

            # 1️⃣ Glucose Distribution
            fig1, ax1 = plt.subplots()
            sns.histplot(data["Glucose"], kde=True, ax=ax1)
            ax1.set_title("Glucose Distribution")
            st.pyplot(fig1)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>🧪 High glucose concentration is the strongest predictor of diabetes.</p>",
    unsafe_allow_html=True
)

            # 2️⃣ BMI Distribution
            fig2, ax2 = plt.subplots()
            sns.histplot(data["BMI"], kde=True, ax=ax2)
            ax2.set_title("BMI Distribution")   
            st.pyplot(fig2)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>🧪 Increased BMI contributes to insulin resistance.</p>",
    unsafe_allow_html=True
)

            # 3️⃣ Age Distribution
            fig3, ax3 = plt.subplots()
            sns.histplot(data["Age"], kde=True, ax=ax3)
            ax3.set_title("Age Distribution")
            st.pyplot(fig3)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>🧪 Diabetes prevalence increases with age due to metabolic decline.</p>",
    unsafe_allow_html=True
)

            # 4️⃣ Glucose vs BMI
            fig4, ax4 = plt.subplots()
            sns.scatterplot(x=data["Glucose"], y=data["BMI"], ax=ax4)
            ax4.set_title("Glucose vs BMI")
            st.pyplot(fig4)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>🧪 Higher glucose and obesity together amplify diabetes risk.</p>",
    unsafe_allow_html=True
    )

            # 5️⃣ Correlation Heatmap
            fig5, ax5 = plt.subplots()
            sns.heatmap(data.corr(), ax=ax5)
            ax5.set_title("Correlation Heatmap")
            st.pyplot(fig5)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>🧪 Correlation heatmap highlights major predictors influencing diabetic outcome.</p>",
    unsafe_allow_html=True
    )

        # 📄 Report Download (Both Roles)
        pdf = generate_report(name,"Diabetes",risk,level,diet,lifestyle)

        st.download_button(
            "📄 Download Report",
            data=pdf,
            file_name=f"{name}_Diabetes_Report.pdf",
            mime="application/pdf"
        )
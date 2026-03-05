import streamlit as st
import pandas as pd
import joblib
import os
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from modules.report_generator import generate_report

BASE = os.path.dirname(os.path.dirname(__file__))

def run_hypertension(role):

    st.header("💓 Hypertension Prediction")

    model = joblib.load(os.path.join(BASE, "Hypertension", "hypertension_model.pkl"))
    feature_cols = joblib.load(os.path.join(BASE, "Hypertension", "feature_columns.pkl"))

    name = st.text_input("Patient Name")

    input_data = {}
    for col in feature_cols:
        input_data[col] = st.number_input(col, value=0.0)

    if st.button("Predict Hypertension Risk"):

        df = pd.DataFrame([input_data])
        prob = model.predict_proba(df)[0][1]
        risk = round(prob * 100, 2)

        # ------------------ Gauge ------------------
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk,
            title={'text': "Risk Level (%)"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

        # ------------------ Risk Logic ------------------
        if prob < 0.3:
            level = "Low Risk"
            diet = "Low salt diet recommended."
            lifestyle = "Daily 30 min walking."
        elif prob < 0.6:
            level = "Moderate Risk"
            diet = "Reduce sodium and processed foods."
            lifestyle = "Monitor BP regularly."
        else:
            level = "High Risk"
            diet = "Strict DASH diet plan."
            lifestyle = "Immediate physician consultation advised."

        st.success(f"Risk: {risk}%")
        st.info(f"Level: {level}")
        st.write("🥗 Diet:", diet)
        st.write("🏃 Lifestyle:", lifestyle)

        # ------------------ Doctor Section ------------------
        if role == "Doctor":

            st.subheader("📊 Clinical Analytics")

            data = pd.read_csv(
                os.path.join(BASE, "Hypertension", "hypertension_dataset.csv")
            )

            # 1️⃣ Age Distribution
            fig1, ax1 = plt.subplots()
            sns.histplot(data["Age"], kde=True, ax=ax1)
            ax1.set_title("Age Distribution")
            st.pyplot(fig1)
            st.markdown(
                "<p style='font-size:25px; font-weight:600;'>🩺 Hypertension prevalence increases significantly with age.</p>",
                unsafe_allow_html=True
            )

            # 2️⃣ BMI Distribution
            fig2, ax2 = plt.subplots()
            sns.histplot(data["BMI"], kde=True, ax=ax2)
            ax2.set_title("BMI Distribution")
            st.pyplot(fig2)
            st.markdown(
                "<p style='font-size:25px; font-weight:600;'>🩺 Elevated BMI contributes to increased blood pressure.</p>",
                unsafe_allow_html=True
            )

       
            # 3️⃣ Stress Score Distribution
            fig3, ax3 = plt.subplots()
            sns.histplot(data["Stress_Score"], kde=True, ax=ax3)
            ax3.set_title("Stress Score Distribution")
            st.pyplot(fig3)

            st.markdown(
    "<p style='font-size:25px; font-weight:600;'>🩺 Higher stress levels contribute to sustained high blood pressure.</p>",
    unsafe_allow_html=True
)

            # 4️⃣ Age vs BMI
            fig4, ax4 = plt.subplots()
            sns.scatterplot(x=data["Age"], y=data["BMI"], ax=ax4)
            ax4.set_title("Age vs BMI")
            st.pyplot(fig4)
            st.markdown(
                "<p style='font-size:25px; font-weight:600;'>🩺 Combined increase in age and BMI elevates hypertension risk.</p>",
                unsafe_allow_html=True
            )

            # 5️⃣ Correlation Heatmap (Numeric Only)
            fig5, ax5 = plt.subplots()
            numeric_data = data.select_dtypes(include=["int64", "float64"])
            corr_matrix = numeric_data.corr()

            sns.heatmap(corr_matrix, ax=ax5, cmap="coolwarm")
            ax5.set_title("Correlation Matrix")
            st.pyplot(fig5)
            st.markdown(
                "<p style='font-size:25px; font-weight:600;'>🩺 Heatmap highlights strongest numeric predictors of hypertension risk.</p>",
                unsafe_allow_html=True
            )

        # ------------------ Report Download ------------------
        pdf = generate_report(name, "Hypertension", risk, level, diet, lifestyle)

        st.download_button(
            "📄 Download Report",
            data=pdf,
            file_name=f"{name}_Hypertension_Report.pdf",
            mime="application/pdf"
        )
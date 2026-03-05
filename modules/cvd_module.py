import streamlit as st
import pandas as pd
import joblib
import os
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from modules.report_generator import generate_report

BASE = os.path.dirname(os.path.dirname(__file__))

def run_cvd(role):

    st.header("❤️ Cardiovascular Disease Prediction")

    model = joblib.load(os.path.join(BASE,"cvd","cvd_model.pkl"))
    feature_cols = joblib.load(os.path.join(BASE,"cvd","feature_columns.pkl"))

    name = st.text_input("Patient Name")

    input_data = {}
    for col in feature_cols:
        input_data[col] = st.number_input(col, value=0.0)

    if st.button("Predict CVD Risk"):

        df = pd.DataFrame([input_data])
        prob = model.predict_proba(df)[0][1]
        risk = round(prob*100,2)

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk,
            title={'text':"Risk Level (%)"},
            gauge={'axis':{'range':[0,100]}}
        ))
        st.plotly_chart(fig,use_container_width=True)

        # Risk Logic
        if prob < 0.3:
            level="Low Risk"
            diet="Low fat balanced diet."
            lifestyle="Regular walking 30 min daily."
        elif prob < 0.6:
            level="Moderate Risk"
            diet="Reduce cholesterol & oil intake."
            lifestyle="Monthly cardiovascular checkup."
        else:
            level="High Risk"
            diet="Strict heart-friendly diet plan."
            lifestyle="Immediate cardiologist consultation required."

        st.success(f"Risk: {risk}%")
        st.info(f"Level: {level}")
        st.write("🥗 Diet:", diet)
        st.write("🏃 Lifestyle:", lifestyle)

        # 🔵 Doctor Section
        if role == "Doctor":

            st.subheader("📊 Clinical Analytics")

            data = pd.read_csv(
                os.path.join(BASE,"cvd","cleaned_cardio_data.csv")
            )

            # 1️⃣ Age Distribution
            fig1, ax1 = plt.subplots()
            sns.histplot(data["age"], kde=True, ax=ax1)
            ax1.set_title("Age Distribution")
            st.pyplot(fig1)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>❤️ Cardiovascular risk increases significantly with age due to arterial stiffness.</p>",
    unsafe_allow_html=True
)

            # 2️⃣ Cholesterol
            fig2, ax2 = plt.subplots()
            sns.histplot(data["cholesterol"], kde=True, ax=ax2)
            ax2.set_title("Cholesterol Levels")
            st.pyplot(fig2)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>❤️ Elevated cholesterol contributes to artery blockage and heart disease.</p>",
    unsafe_allow_html=True
)

            # 3️⃣ Blood Pressure
            fig3, ax3 = plt.subplots()
            sns.histplot(data["ap_hi"], kde=True, ax=ax3)
            ax3.set_title("Systolic Blood Pressure Distribution")
            st.pyplot(fig3)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>❤️ High systolic blood pressure strongly correlates with CVD risk.</p>",
    unsafe_allow_html=True
    )

            # 4️⃣ Age vs Cholesterol
            fig4, ax4 = plt.subplots()
            sns.scatterplot(x=data["age"], y=data["cholesterol"], ax=ax4)
            ax4.set_title("Age vs Cholesterol")
            st.pyplot(fig4)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>❤️ Combined high cholesterol and age elevate cardiac risk.</p>",
    unsafe_allow_html=True
    )

            # 5️⃣ Correlation Heatmap
            fig5, ax5 = plt.subplots()
            sns.heatmap(data.corr(), ax=ax5)
            ax5.set_title("Correlation Heatmap")
            st.pyplot(fig5)
            st.markdown(
    "<p style='font-size:25px; font-weight:500;'>❤️ Correlation matrix highlights dominant CVD predictors.</p>",
    unsafe_allow_html=True
    )

        # 📄 Report Download (Both Roles)
        pdf = generate_report(name,"CVD",risk,level,diet,lifestyle)

        st.download_button(
            "📄 Download Report",
            data=pdf,
            file_name=f"{name}_CVD_Report.pdf",
            mime="application/pdf"
        )
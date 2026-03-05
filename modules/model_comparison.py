import streamlit as st
import pandas as pd
import plotly.express as px

def run_model_comparison():

    st.header("📊 Model Performance Comparison")

    data = pd.DataFrame({
        "Disease": [
            "Diabetes",
            "Diabetes",
            "Diabetes",
            "Hypertension",
            "Hypertension",
            "Hypertension",
            "CVD",
            "CVD",
            "CVD"
        ],
        "Model": [
            "Logistic Regression",
            "SVM",
            "Random Forest",
            "Logistic Regression",
            "SVM",
            "Random Forest",
            "Logistic Regression",
            "SVM",
            "Random Forest"
        ],
        "Accuracy": [
            0.70,
            0.73,
            0.77,
            0.87,
            0.88,
            0.94,
            0.69,
            0.72,
            0.71
        ]
    })

    st.dataframe(data)

    fig = px.bar(
        data,
        x="Disease",
        y="Accuracy",
        color="Model",
        barmode="group",
        title="Accuracy Comparison Across Models"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    🔎 Random Forest performs best overall.
    Hypertension dataset achieved highest accuracy (0.94).
    """)
import streamlit as st
import matplotlib.pyplot as plt

def show_plot(title, plot_function, explanation):
    st.subheader(title)

    fig, ax = plt.subplots()
    plot_function(ax)

    st.pyplot(fig)
    plt.close(fig)

    st.info(explanation)

import streamlit as st

st.markdown(
        """
        <div style='font-size: 18px; line-height: 1.6;'>
            <h3 style='font-weight: bold;'>Welcome to Xerophyta Data Explorer!</h3>
            <p>This tool simplifies the exploration of our transcriptomic datasets. Quickly find Xerophyta genes using Arabidopsis symbols/IDs, GO terms, or protein domains, allowing you to focus on your genes of interest.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
# st.image("images/seedling.jpg")
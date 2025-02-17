import streamlit as st

st.markdown(
        """
       
            # Welcome to Xerophyta Data Explorer!</h3>
            This tool simplifies the exploration of our transcriptomic datasets. Quickly find Xerophyta genes using Arabidopsis symbols/IDs, GO terms, or protein domains, allowing you to focus on your genes of interest.
        """,
        unsafe_allow_html=True
    )
st.image("all_plants.png")


st.divider()

st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")


import streamlit as st


# entry point app 
home_page = st.Page("home.py", title="Home", icon=":material/add_circle:")
expression_page = st.Page("expression_page.py", title="Expression data",)

pg = st.navigation([home_page,expression_page])
st.set_page_config(page_title="Data explorer",page_icon=":material/edit:",layout="wide")

pg.run()
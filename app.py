import streamlit as st


# entry point app 
home_page = st.Page("home.py", title="Home") #icon=":material/add_circle:")
expression_page = st.Page("expression_page.py", title="Expression data",)
gene_query_page = st.Page("gene_query_page.py", title="Gene info",)
test_page = st.Page("test_page.py", title="Test page",)
pg = st.navigation([home_page,expression_page,gene_query_page, test_page])
st.set_page_config(page_title="Data explorer",page_icon=":material/edit:",layout="wide")

pg.run()
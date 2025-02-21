import streamlit as st


# entry point app 
home_page = st.Page("server/home.py", title="Home") #icon=":material/add_circle:")
expression_page = st.Page("server/expression_page.py", title="Expression data",)


# swap out the gene_query_page for the test_page TODO swap the test_page for the gene_query_page at some point
gene_query_page= st.Page("server/gene_query_page.py", title="Gene info",)
pg = st.navigation([home_page,expression_page,gene_query_page])
st.set_page_config(page_title="Data explorer",page_icon=":material/edit:",layout="wide")

pg.run()
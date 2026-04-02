import streamlit as st

st.set_page_config(page_title="Data explorer",page_icon=":material/edit:",layout="wide")

    # entry point app
home_page = st.Page("server/home.py", title="Home", icon="🏠") #icon=":material/add_circle:")
expression_page = st.Page("server/expression_page.py", title="Expression data",icon="📊")
#  TODO swap the test_page for the gene_query_page at some point
gene_query_page= st.Page("server/gene_query_page.py", title="Gene info",icon="📑")
grn_explorer = st.Page("server/grn_explorer.py", title="Gene Regulatory Network", icon="🌐")


pg = st.navigation([home_page,expression_page,gene_query_page, grn_explorer])

pg.run()


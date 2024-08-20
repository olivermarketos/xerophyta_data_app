import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import data_connector
import plots

st.title('Xerophyta Data Explorer')


dataset_options=["X. elegans","X. humilis"]
gene_selection_options = ['Xerophyta GeneID', "Arabidopsis ortholog", "Genes with GO term", "Genes with protein domain"]
deg_options = ["show all genes", "Only display DEGS", "Only display up-regulted DEGs", "Only display down-regulated DEGs"]
genes_to_plot = ['Xele.ptg000001l.1', 'Xele.ptg000001l.116','Xele.ptg000001l.16']
data = pd.read_csv("data/Xe_seedlings_normalised_counts_tidy.csv")



@st.cache_data
def show_raw_data(df, genes):

    filtered_df = df[df['gene_name'].isin(genes)]

    st.subheader("Raw Data")
    st.write(
        filtered_df
    )
dataset = st.sidebar.selectbox(
    "Select a dataset:",
    dataset_options
)

if st.checkbox("Show raw data"): 
    show_raw_data(data, genes_to_plot)
   

st.subheader("Plot")

plt = plots.expression_plot(pd.DataFrame(data), genes_to_plot)

st.pyplot(plt)

gene_selection = st.sidebar.selectbox(
    "Gene selection method:",
    gene_selection_options
)

filter_degs = st.sidebar.selectbox(
    "Do you wish to filter gene based on differential expression?",
    deg_options
)

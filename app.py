import streamlit as st
import pandas as pd
import numpy as np



dataset_options=["Wachendorfia","Xerophyta"]
gene_selection_options = ['Xerophyta GeneID', "Arabidopsis ortholog", "Genes with GO term", "Genes with protein domain"]
deg_options = ["show all genes", "Only display DEGS", "Only display up-regulted DEGs", "Only display down-regulated DEGs"]


dataset = st.selectbox(
    "Select a dataset:",
    dataset_options
)

gene_selection = st.selectbox(
    "Gene selection method:",
    gene_selection_options
)

filter_degs = st.selectbox(
    "Do you wish to filter gene based on differential expression?",
    deg_options
)

# max_genes = 

# plot_options = 



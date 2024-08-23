import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import data_connector
import plots

st.title('Xerophyta Data Explorer')
st.divider()

###############################
# Place holders and tags 
###############################

options_dataset=["X. elegans time-series","foo"]
options_gene_selection = ['Xerophyta GeneID', "Arabidopsis ortholog", "Genes with GO term", "Genes with protein domain"]
options_deg = ["show all genes", "Only display DEGS", "Only display up-regulted DEGs", "Only display down-regulated DEGs"]

genes_to_plot = ['Xele.ptg000001l.1', 'Xele.ptg000001l.116','Xele.ptg000001l.16']
place_holder_genes= "Xele.ptg000001l.1, Xele.ptg000001l.116,Xele.ptg000001l.16"
data = pd.read_csv("data/Xe_seedlings_normalised_counts_tidy.csv")


###############################
#Functions 
###############################

@st.cache_data
def show_raw_data(df, genes):

    filtered_df = df[df['gene_name'].isin(genes)]

    st.subheader("Raw Data")
    st.write(
        filtered_df
    )

def convert_At_to_Xe_ID(genes):
    pass

def home_page():
    st.text("Fill in values on the left then click generate")

def generate_plots():
    st.write(f"selected options are: {st.session_state}")
    st.subheader("Plot")
    st.text(', '.join(input_genes))

    plt = plots.expression_plot(pd.DataFrame(data), input_genes)

    st.pyplot(plt)
    st.divider()
    if st.checkbox("Show raw data"): 
        show_raw_data(data, genes_to_plot)
###############################
#Side Bar
###############################

if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False

st.sidebar.radio(
    "Select a dataset:",
    options_dataset, 
    key="dataset")


st.sidebar.radio(
    "Gene selection method:",
    options_gene_selection,
    key="gene_selection")


if st.session_state.gene_selection =="Xerophyta GeneID":
    input_genes=st.sidebar.text_input("Enter Xerophyta GeneIDs separated by  a comma.",place_holder_genes)
    input_genes = [item.strip() for item in input_genes.split(',')]

elif st.session_state.gene_selection =="Arabidopsis ortholog":
    input_genes=st.sidebar.text_input("Enter Arabidopsis orthologues separated by  a comma.","ERF1, WRKY33, AT1G55020, AT5G42650")
    convert_At_to_Xe_ID(input_genes)
    input_genes = genes_to_plot

elif st.session_state.gene_selection =="Genes with GO term":
    input_genes=st.sidebar.text_input("Enter GO term description or ID separated by  a comma.","jasmonic acid mediated signaling pathway")
    input_genes = genes_to_plot

elif st.session_state.gene_selection == "Genes with protein domain":
    input_genes=st.sidebar.text_input("Enter protein domains to search for, separated by  a comma.",)
    input_genes = genes_to_plot


st.sidebar.radio(
    "Do you wish to filter gene based on differential expression?",
    options_deg,
    key="filter_degs")

st.write(st.session_state)


if(st.sidebar.button(label="Generate")):
    st.session_state.generate_clicked = True 
    generate_plots()

else:
    home_page()
###############################
# End Side Bar
###############################




st.divider()

st.caption("For any issues or inquiries, please contact us at [**which email address?**].")
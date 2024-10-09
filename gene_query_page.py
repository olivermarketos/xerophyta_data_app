import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import  db
import plots

import re

st.title('Xerophyta Data Explorer')
st.divider()

###############################
# Place holders and tags 
###############################

options_dataset=["X. elegans time-series"]
# options_gene_selection = ['Xerophyta GeneID', "Arabidopsis ortholog", "Genes with GO term", "Genes with protein domain"]
options_gene_selection = ['Xerophyta GeneID', "Arabidopsis ortholog"]
options_deg = ["show all genes"]
options_plot_type = ["Genes on single plot", "Genes on separate plot"]
# options_deg = ["show all genes", "Only display DEGS", "Only display up-regulted DEGs", "Only display down-regulated DEGs"]

genes_to_plot = ['Xele.ptg000001l.1', 'Xele.ptg000001l.116','Xele.ptg000001l.16']
place_holder_genes= "Xele.ptg000001l.1, Xele.ptg000001l.116,Xele.ptg000001l.16"


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


def instruction_page():

    # Welcome and brief introduction
    

    # Detailed steps and descriptions
    st.markdown(
        """
        #### **Step 1: Select your dataset to analyse**

        - **Time-series expression:** Explore dynamic expression profiles ...
        
        #### **Step 2: Select your genes of interest**

        - **Lettuce GeneID:** Input Lettuce gene ID(s).
        - **Orthologues of Arabidopsis Genes:** Provide an Arabidopsis gene ID ...
        - **Genes with GO-term:** Enter a GO term ...
        - **Genes with Protein Domain:** Search genes ...

        #### **Step 3: Dataset-specific options**

        - Dataset-specific gene selection criteria ...
        - Plot customisation options ...

        #### **Step 4: Click 'Generate'**
        """
    )

def retreive_gene_info():
    database = db.DB()

    input_genes = re.split(r'[\s,]+', st.session_state.input_genes.strip())
    
    if st.session_state.gene_input_type == "Gene_ID":
        input_genes = database.get_gene_from_arab_homolog(input_genes)
        input_genes = [x[0] for x in input_genes]
    
    elif st.session_state.gene_input_type == "Arab_homolog":
        matches = database.match_homologue_to_Xe_gene(input_genes)
        st.dataframe(matches, use_container_width=True)




if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False

if 'gene_input_type' not in st.session_state:
    st.session_state.gene_input_type = "Gene_ID"

st.sidebar.radio(
    "Select a dataset:",
    options_dataset, 
    key="dataset")


st.sidebar.radio(
    "Gene selection method:",
    options_gene_selection,
    key="gene_selection")


if st.session_state.gene_selection =="Xerophyta GeneID":
    st.sidebar.text_input("Enter Xerophyta GeneIDs separated by  a comma.",place_holder_genes, key="input_genes")
    st.session_state.gene_input_type = "Gene_ID"

elif st.session_state.gene_selection =="Arabidopsis ortholog":
    st.sidebar.text_area("Enter Arabidopsis orthologues separated by  a comma.","At4g12010, OXA1", key="input_genes")
    st.session_state.gene_input_type = "Arab_homolog"






if(st.sidebar.button(label="Generate")):
    st.session_state.generate_clicked = True
    retreive_gene_info()




###############################
# End Side Bar
###############################




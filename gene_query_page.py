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



def instruction_page():

    # Welcome and brief introduction
    

    # Detailed steps and descriptions
    st.markdown(
        """
        #### Retrieve gene annotation data from _X. elegan_ genes by directly querying  _X. elegans_ gene IDs or by _Arabidopsis_ homologues.
        """
    )

def retreive_gene_info():
    database = db.DB()

    input_genes = re.split(r'[\s,]+', st.session_state.input_genes.strip())
    
    if st.session_state.gene_input_type == "Gene_ID":
        st.markdown(
        """
        #### Retreived data from  _X. elegans_ gene ID query.
        Empty rows indicate that the gene <had no match from B2Go?>>.

        Information can be downloaded with the button on the top right of the table.
        """)

    elif st.session_state.gene_input_type == "Arab_homolog":
        matches = database.match_homologue_to_Xe_gene(input_genes)
        input_genes = matches["X. elegans gene"].to_list()
        st.markdown(
        """
        #### Retreived data based on _Arabidopsis_ homologues.
        Table of queries and associated homologues. Empty rows indicate that no exact match to the provided _At_ gene name  was found.
        """)

        st.dataframe(matches, use_container_width=True)

    query = database.get_gene_annotation_data(input_genes)

    data = [row.__dict__ for row in query]
    # Remove SQLAlchemy internal state
    for item in data:
        item.pop('_sa_instance_state', None)

    # Convert to a DataFrame
    if data:
        df = pd.DataFrame(data)
        df = df[['gene_name',
                'sequence_description',
                'nt_sequence',
                'Alignment_length',
                'blast_min_e_value',  'Hit_ACC', 'Bit_Score', 'Positives', 'Similarity' ]  ] 
        st.dataframe(df)
        print(df.columns.tolist())

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
    st.sidebar.text_area("Enter Xerophyta GeneIDs separated by  a comma.",place_holder_genes, key="input_genes")
    st.session_state.gene_input_type = "Gene_ID"

elif st.session_state.gene_selection =="Arabidopsis ortholog":
    st.sidebar.text_area("Enter Arabidopsis orthologues separated by a comma, space or each entry on new line.","At4g12010, OXA1", key="input_genes")
    st.session_state.gene_input_type = "Arab_homolog"



if(st.sidebar.button(label="Generate")):
    st.session_state.generate_clicked = True
    retreive_gene_info()
else:
    instruction_page()



st.divider()

st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")


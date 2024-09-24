import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plots
import db
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
    st.subheader("Instruction page")
    st.text("Fill in values on the left then click generate")

def retreive_expression_data():
    database = db.DB()
    input_genes = [item.strip() for item in st.session_state.input_genes.split(',')]
    
    if st.session_state.gene_input_type == "Arab_homolog":
        input_genes = database.get_gene_from_arab_homolog(input_genes)
        input_genes = [x[0] for x in input_genes]

    data = database.get_gene_expression_data(input_genes)
    return data




def generate_plots(data):
    st.subheader("Plot")

    if st.session_state.plot_type == "Genes on single plot":
        figures = plots.single_panel_gene_expression(data, st.session_state.expression_values)
        col1, col2 = st.columns(2)  # Create two columns for side-by-side plots

        # Show the first plot in the left column
        with col1:
            st.pyplot(figures[0])

        # Show the second plot in the right column
        with col2:
            st.pyplot(figures[1])
   
   
    # plot on separate panels
    else:
        figures = plots.multi_panel_gene_expression(data, st.session_state.expression_values)
        # Group the figures by gene_name
        grouped_figures = {}

        for fig in figures:
            # Extract the gene name from the title
            title = fig.axes[0].get_title()
            gene_name = title.split('|')[0].strip()  
            if gene_name not in grouped_figures:
                grouped_figures[gene_name] = []

            grouped_figures[gene_name].append(fig)

        # Display plots for each gene, side by side
        for gene_name, gene_figures in grouped_figures.items():
            if len(gene_figures) == 2:
                col1, col2 = st.columns(2)  # Create two columns for side-by-side plots

                # Show the first plot in the left column
                with col1:
                    st.pyplot(gene_figures[0])

                # Show the second plot in the right column
                with col2:
                    st.pyplot(gene_figures[1])
            else:
                # If there's only one figure for a gene, show it in full width
                st.pyplot(gene_figures[0])

###############################
#Side Bar
###############################

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
    st.sidebar.text_input("Enter Arabidopsis orthologues separated by  a comma.","At4g12010, OXA1", key="input_genes")
    st.session_state.gene_input_type = "Arab_homolog"


elif st.session_state.gene_selection =="Genes with GO term":
    st.sidebar.text_input("Enter GO term description or ID separated by  a comma.","jasmonic acid mediated signaling pathway", key="input_genes")

elif st.session_state.gene_selection == "Genes with protein domain":
    st.sidebar.text_input("Enter protein domains to search for, separated by  a comma.", key="input_genes")


# st.sidebar.radio(
#     "Do you wish to filter gene based on differential expression?",
#     options_deg,
#     key="filter_degs")

st.sidebar.radio(
    "Dp you want to plot log2fc or normalised expression values?",
    ["log2_expression", "normalised_expression"],
    key="expression_values")

st.sidebar.radio(
    "How would you like the expression plots to be displayed?",
    options_plot_type,
    key="plot_type")



if(st.sidebar.button(label="Generate")):
    st.session_state.generate_clicked = True
    if st.session_state.input_genes:
        data = retreive_expression_data()
        generate_plots(data)
    else:
        st.write("Please enter gene names")

else:
    instruction_page()


###############################
# End Side Bar
###############################

st.divider()

st.caption("For any issues or inquiries, please contact us at olivermarketos@gmail.com.")



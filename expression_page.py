import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import  db
import plots

st.title('Xerophyta Data Explorer')
st.divider()

database = db.DB()
EXPRESSION_PLOT_OPTIONS = ["log2_expression", "normalised_expression"]
PLOT_DISPLAY_OPTIONS = ["Genes on single plot", "Genes on separate plot"]
GENE_SELECTION_OPTIONS = {
    "Xerophyta GeneID": {
        "placeholder": "Xele.ptg000001l.1, Xele.ptg000001l.116",
        "key": "Gene_ID",
        "input_label": "Enter Xerophyta GeneIDs separated by commas, space or newline:"
    },
    "Arabidopsis ortholog": {
        "placeholder": "At4g32010, OXA1",
        "key": "Arab_homolog",
        "input_label": "Enter Arabidopsis orthologues separated by commas, space or newline:"
    },
    "Genes with GO term": {
        "key": "GO_term",
        "placeholder": "jasmonic acid mediated signaling pathway",
        "input_label": "Enter GO term description or ID separated by commas, space or newline:"
    }
}


def initialise_session_state():
    if "generate_clicked" not in st.session_state:
        st.session_state.generate_clicked = False
    if "input_genes" not in st.session_state:
        st.session_state.input_genes = ""
    if "show_raw_data" not in st.session_state:
        st.session_state.show_raw_data = False

def setup_sidebar():

    # Define selection options
    species = [species.name for species in database.get_species()]
    selected_species = st.sidebar.radio("Select a species:", species, key="species")
    
    experiments = [experiment.experiment_name for experiment in database.get_experiments_by_species(selected_species)]
    selected_experiment = st.sidebar.radio("Select a dataset:", experiments, key="experiment")
    
    selected_gene_selection = st.sidebar.radio("Gene selection method:", list(GENE_SELECTION_OPTIONS.keys()), key="gene_selection")

    # Gene input field based on selection
    for option, config in GENE_SELECTION_OPTIONS.items():
        if selected_gene_selection == option:
            st.sidebar.text_area(
                config["input_label"],
                placeholder=config["placeholder"],
                key="input_genes",
                value = st.session_state.input_genes,
                on_change=lambda: st.session_state.update({"input_genes": st.session_state.input_genes})  # Update session state on change
            )
            st.session_state.gene_input_type = config["key"]

    # Plot options
    st.sidebar.radio("Expression value to plot:", EXPRESSION_PLOT_OPTIONS, key="expression_values")
    st.sidebar.radio("Plot display style:", PLOT_DISPLAY_OPTIONS, key="plot_type")
    

def show_instructions():
    st.markdown(
        """
        #### **Step 1: Select your species and dataset to analyse**

        - **Time-series expression:** Explore dynamic expression profiles
        
        #### **Step 2: Select your genes of interest**

        - **Xerophyta GeneID:** Input Xerophyta gene ID(s)
        - **Orthologues of Arabidopsis Genes:** Provide an Arabidopsis gene ID
        - **Genes with GO-term:** Enter a GO term
        """
       
    )

@st.cache_data
def show_raw_data(data):
    df = data[[  "gene_name", "log2_expression", "normalised_expression", "treatment", "time",  "replicate"]]
    st.dataframe(df)



def process_input_genes(input_genes):
    """
    Splits the user's input (comma, space, newline) into a list of unique, non-empty strings.
    """
    if not input_genes.strip():
        return []
    # Replace commas/newlines with spaces
    cleaned = input_genes.replace(",", " ").replace("\n", " ")
    # Split on whitespace
    tokens = [t.strip() for t in cleaned.split(" ") if t.strip()]
    # Return unique tokens
    return list(set(tokens))

def map_gene_selection():
    """
    Maps the gene selection method to the appropriate function.
    """
    gene_selection = {
        "Xerophyta GeneID": "xerophyta",
        "Arabidopsis ortholog": "arabidopsis",
        "Genes with GO term": "go_term"
    }
    return gene_selection[st.session_state.gene_selection]

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


def show_missing_genes(genes):
    if genes:
        st.warning(f"The following gene(s) are not in the database: {', '.join(genes)}")

def main():
    initialise_session_state()
    setup_sidebar()

    if st.sidebar.button("Generate"):
        st.session_state.generate_clicked = True
 
    if st.session_state.generate_clicked:
        input_genes = process_input_genes(st.session_state.input_genes)
        # input_genes = st.session_state.input_genes
        if input_genes:

            gene_selection = map_gene_selection()

            if gene_selection == "xerophyta":
                in_database = database.check_if_gene_in_database(input_genes)
                genes_in_db = []
                genes_not_in_db = []

                for gene, is_in_db in zip(input_genes, in_database):
                    if is_in_db:
                        genes_in_db.append(gene)
                    else:
                        genes_not_in_db.append(gene)

                rna_seq_data = database.get_gene_expression_data(genes_in_db, st.session_state.experiment)
                
                show_missing_genes(genes_not_in_db)
                if rna_seq_data.empty:
                    st.warning("No data found for the selected genes.")
                else:
                    generate_plots(rna_seq_data)

                if st.checkbox("Show raw data"):
                    show_raw_data(rna_seq_data)

            elif gene_selection == "arabidopsis":
                pass

            elif gene_selection == "go_term":
                in_database = database.check_if_go_term_in_database(input_genes)
                terms_in_db = []
                terms_not_in_db = []
                st.write(in_database)
                st.write(input_genes)


        else:
            st.markdown("Please enter at least one gene ID")


    else:
        show_instructions()


main()
st.divider()
st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")




# def match_genes(input_genes):
    
#     database = db.DB()
#     return  database.match_homologue_to_Xe_gene(input_genes)







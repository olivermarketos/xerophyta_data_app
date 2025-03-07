import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import  database.db as db
import utils.plots as plots
from utils.constants import DEGFilter, GENE_SELECTION_OPTIONS, DEG_FILTER_OPTIONS
from utils.helper_functions import parse_input, retreive_query_data
from datetime import datetime
import io, zipfile

st.title('Xerophyta Data Explorer')
st.divider()

database = db.DB()
EXPRESSION_PLOT_OPTIONS = ["log2_expression", "normalised_expression"]
PLOT_DISPLAY_OPTIONS = ["Genes on single plot", "Genes on separate plot"]


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
                value=config["value"],
                key="input_genes",
                on_change=lambda: st.session_state.update({"input_genes": st.session_state.input_genes})  # Update session state on change
            )
            st.session_state.gene_input_type = config["key"]

    # Plot options
    st.sidebar.radio("Expression value to plot:", EXPRESSION_PLOT_OPTIONS, key="expression_values")
    st.sidebar.radio(
        "Filter genes based on differential expression:",
        list(DEG_FILTER_OPTIONS.keys()),  # Display text in the sidebar
        key="filter_deg"
        )
    st.sidebar.radio("Plot display style:", PLOT_DISPLAY_OPTIONS, key="plot_type")
    



@st.cache_data
def show_raw_data(data):
    df = data[[  "gene_name", "log2_expression", "normalised_expression", "treatment", "time",  "replicate"]]
    st.dataframe(df)


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
    st.subheader("Plots")

    if st.session_state.plot_type == "Genes on single plot":
    # Create one combined figure with two side-by-side panels and a shared legend
        fig = plots.dual_panel_gene_expression(data, st.session_state.expression_values)
        st.pyplot(fig)

    # Save the figure to a bytes buffer in PNG format.
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)  # Move to the beginning of the BytesIO buffer

        # Provide a download button for the combined plot.
        st.download_button(
            label="Download combined plot",
            data=buf,
            file_name="combined_plot.png",
            mime="image/png"
        )
        plt.close(fig)
    # plot on separate panels
    else:
        # Generate figures
        figures = plots.multi_panel_gene_expression(data, st.session_state.expression_values)
        
        # Group the figures by gene_name
        grouped_figures = {}
        for fig in figures:
            # Extract the gene name from the title
            title = fig.axes[0].get_title()
            gene_name = title.split('|')[0].strip()  
            grouped_figures.setdefault(gene_name, []).append(fig)

        # Display plots for each gene, side by side
        for gene_name, gene_figures in grouped_figures.items():
            if len(gene_figures) == 2:
                col1, col2 = st.columns(2)  # Create two columns for side-by-side plots
                with col1:
                    st.pyplot(gene_figures[0])
                with col2:
                    st.pyplot(gene_figures[1])
            else:
                # If there's only one figure for a gene, show it full width
                st.pyplot(gene_figures[0])
        
        # Create a ZIP file containing all plots
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for gene_name, gene_figures in grouped_figures.items():
                # Use a safe name; adjust splitting as needed
                parts = gene_name.split(" ")
                name = parts[1] if len(parts) > 1 else gene_name
                if len(gene_figures) == 2:
                    buf1 = io.BytesIO()
                    gene_figures[0].savefig(buf1, format='png', bbox_inches='tight')
                    buf1.seek(0)
                    zipf.writestr(f"{name}_dehydration.png", buf1.getvalue())
                    buf1.close()

                    buf2 = io.BytesIO()
                    gene_figures[1].savefig(buf2, format='png', bbox_inches='tight')
                    buf2.seek(0)
                    zipf.writestr(f"{name}_rehydration.png", buf2.getvalue())
                    buf2.close()
                else:
                    buf = io.BytesIO()
                    gene_figures[0].savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    zipf.writestr(f"{name}_plot.png", buf.getvalue())
                    buf.close()

        zip_buffer.seek(0)
        st.download_button(
            label="Download all plots",
            data=zip_buffer,
            file_name="all_plots.zip",
            mime="application/zip"
        )
        zip_buffer.close()

        # Finally, close all figures to free memory.
        for gene_figures in grouped_figures.values():
            for fig in gene_figures:
                plt.close(fig)


def empty_genes_warning():
    st.warning("No data found for the selected genes. Please double check that the correct boxes on the left are selected and that the entered terms are correct.")

def show_missing_genes(genes):
    if genes:
        st.warning(f"The following gene(s) are not in the database: {', '.join(genes)}")

def main():
    initialise_session_state()


    if st.sidebar.button("Generate plots"):
        st.session_state.generate_clicked = True
 
    if st.sidebar.button("Show Instructions") or not st.session_state.generate_clicked:
        show_instructions()
        st.session_state.generate_clicked = False

    setup_sidebar()

    if st.session_state.generate_clicked:
        input_genes = st.session_state.input_genes
        # input_genes = st.session_state.input_genes
        if input_genes:
            selected_species = st.session_state.species
            input_genes = parse_input(input_genes)
            rna_seq_data = []

            gene_data, matched_input, missing_input = retreive_query_data(input_genes, selected_species, st.session_state.gene_input_type)
            
            xerophyta_genes = [gene.gene_name for gene in gene_data]           

            # Fetch RNA-seq data and apply DEG filtering
            selected_filter = DEG_FILTER_OPTIONS[st.session_state.filter_deg]
            rna_seq_data = database.get_gene_expression_data(
                xerophyta_genes, 
                st.session_state.experiment, 
                filter_deg=selected_filter
            )

            show_missing_genes(missing_input)
               
            if rna_seq_data.empty:
                empty_genes_warning()
            else:
                with st.spinner("Generating plots...", show_time=True):
                    generate_plots(rna_seq_data)
                    num_genes_retreived = rna_seq_data['gene_name'].nunique()
                    st.write(f"Found {num_genes_retreived} gene(s).")

            if st.checkbox("Show raw data"):
                show_raw_data(rna_seq_data)
                if not rna_seq_data.empty:
                    csv_data = rna_seq_data.to_csv(index=False)
                else:
                    csv_data = "No data was retrieved from the database. Please double-check your input."
                timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_name = f"Xerophyta_gene_expression_results_{timestamp_str}.csv"
            
                st.download_button(
                    label="Download raw data as CSV",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv"
                )

        else:
            st.markdown("Please enter at least one gene ID")


def show_instructions():
    st.markdown(
        """
        #### **Step 1: Select your species and dataset to analyse**

        - **Time-series expression:** Explore dynamic expression profiles
        
        #### **Step 2: Select your genes of interest**

        - **Xerophyta GeneID:** Input Xerophyta gene ID(s) 
            - e.g. Xele.ptg000049l.138, Xele.ptg000049l.140, Xele.ptg000049l.52
        - **Arabidopsis homologue locus:** Provide an Arabidopsis locus ID 
            - e.g. At5g65540, At5g58510
        - **Arabidopsis homologue common name:** Provide an Arabidopsis common name
            - e.g expansin A4, auxin response factor 2
        - **Query by GO id:**
            - The terms can be with or without a GO branch prefix 
            - e.g. C:GO:0001939 or GO:0001939 will both work.
        - **Query by GO name:**
            - e.g. immune system process, leaf senescence
        - **Query by Enzyme Code:**
            - e.g. EC:1.15.1.1, EC:1.2.3.4
        - **Query by Enzyme Name:**
            - e.g. NAD(+) glycohydrolase, oxalate oxidase
        
        > __note__: \\
            - search terms are **case-insensitive**,\\
            - partial matches are allowed for Arabidopsis homologue common names, GO term descriptions and enzyme names,\\
            - large queries may take longer to process.
            - for GO and enzyme queries, all genes returned will have at least one annotation with a matching term.

        #### **Step 3: Plot settings:**
        - **Expression value to plot:** Choose between log2 expression and normalised expression
        - **Filter genes based on differential expression:** Choose to show all genes, all differentially expressed genes, only up-regulated or down-regulated genes
        - **Plot display style:** Choose to show all genes on a single plot or on separate plots
       #### **Step 4: Generate plots**
        - Click the "Generate" button to retrieve the gene expression information based on the input provided.
        - The plots will be displayed below the input fields.
        - You can also choose to show the raw data by checking the "Show raw data" box.
       """
       
    )

main()
st.divider()
st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")





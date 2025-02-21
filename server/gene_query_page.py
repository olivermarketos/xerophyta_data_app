import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from utils.constants import GENE_SELECTION_OPTIONS

st.title("Xerophyta Database Explorer")
st.divider()
database = db.DB()

# for letting user select what data to display
ALL_COLUMNS = [
            "Species",
            "Xerophyta Gene Name",
            "A. thaliana homologue locus",
            "A. thaliana homologue common name",
            "Gene Description",
            "e-value",
            "similarity",
            "bit_score",
            "alignment_length",
            "positives",
            "GO id",
            "GO name",
            "Enzyme code",
            "Enzyme name",
            "Interpro_id",
            "Interpro GO name"
        ]

def initialise_session_state():
    if "run_query" not in st.session_state:
        st.session_state.run_query = False
    if "input_genes" not in st.session_state:
        st.session_state.input_genes = ""
    # if "species" not in st.session_state:
    #     st.session_state.species = "Any"
    # if "show_raw_data" not in st.session_state:
    #     st.session_state.show_raw_data = False

def setup_sidebar():
    st.sidebar.header("Search Inputs")
    
    # Species selection
    species_list = database.get_species()
    species_options = ["Any"] + [sp.name for sp in species_list]
    selected_species = st.sidebar.selectbox("Select Species (optional):", species_options)
    st.session_state.species = selected_species

    # Query inputs
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

    selected_columns = st.sidebar.multiselect(
        "Select columns to display:", ALL_COLUMNS, default=ALL_COLUMNS)

def parse_multi_input(text_input):
    """
    Splits the user's input (comma, space, newline) into a list of unique, non-empty strings.
    """
    if not text_input.strip():
        return []
    # Replace commas/newlines with spaces
    cleaned = text_input.replace(",", " ").replace("\n", " ")
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


def main():
    initialise_session_state()
    setup_sidebar()

    
    if st.sidebar.button("Run Query"):
        st.session_state.run_query = True
    
    if st.session_state.run_query:
        input_genes = st.session_state.input_genes

        if input_genes:
            gene_selection = map_gene_selection()
            selected_species = st.session_state.species
            st.write(st.session_state)
            results = database.get_gene_annotation_data(input_genes, "xerophyta_gene_name",selected_species)
            df = pd.DataFrame(results)
            st.dataframe(df)        

            st.subheader("Search Results")
            st.write(f"Found {len(results)} gene(s).")
            # st.dataframe(df[selected_columns], use_container_width=True)

            #-------------------------
            # DOWNLOAD BUTTONS
            #-------------------------
            col1, col2 = st.columns(2)
            
            # Download gene data button
            csv_data = df.to_csv(index=False)
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"Xerophyta_gene_query_results_{timestamp_str}.csv"
            
            with col1:
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv"
                )

            # Download FASTA button
            fasta_entries = []
            for g in results:
                # Let’s assume each Gene has .coding_sequence
                seq = g.coding_sequence or ""
                # We'll use the first annotation's description if it exists.
                # If your real models have multiple annotations, adapt the logic below:
                
                # TODO add the descripton to the file name, or add the Arabidopsis homologue
                # desc = g.annotation_description or "No Description"

                # FASTA header: >GeneName description
                header = f">{g.gene_name}"

                # Build the FASTA entry (header + sequence)
                fasta_entries.append(header)
                fasta_entries.append(seq)  # on the next line

            # Join everything with newlines
            fasta_str = "\n".join(fasta_entries)

            
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fasta_filename = f"Xerophyta_genes_{timestamp_str}.fasta"

            with col2:
                st.download_button(
                    label="Download FASTA with coding sequences",
                    data=fasta_str,
                    file_name=fasta_filename,
                    mime="text/plain",  # or "text/fasta"
                )


def instruction_page():

    # Welcome and brief introduction
    # Detailed steps and descriptions
    st.markdown(
        """
        #### Retrieve gene annotation information.

        - The panel on the left provides various means to query the database for gene information.
        - You can query the database using the following methods:
            1. Filter by Xeropyhta species
            2. Query gene ID or arabidopsis homologue (common name or locus ID)
            3. Query GO ID or GO name, Enzyme code or name, or InterPro ID
        """
    )


main()


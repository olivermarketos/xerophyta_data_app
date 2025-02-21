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
            "species",
            "gene_name",
            "a_thaliana_locus",
            "a_thaliana_common_name",
            "description",
            "coding_sequence",
            "e_value",
            "bit_score",
            "similarity",
            "alignment_length",
            "positives",
            "go_ids",
            "go_names",
            "enzyme_codes",
            "enzyme_names",
            "interpro_ids"
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

    st.sidebar.multiselect(
        "Select columns to display:", ALL_COLUMNS, 
        default=ALL_COLUMNS,
        key="selected_columns")

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
        "Arabidopsis homologue locus": "a_thaliana_locus",
        "Arabidopsis homologue common name": "a_thaliana_common_name",
        "Genes with GO term": "go_term"
    }
    return gene_selection[st.session_state.gene_selection]



def main():
    initialise_session_state()
    setup_sidebar()
    instruction_page()
    
    if st.sidebar.button("Run Query"):
        st.session_state.run_query = True
    
    if st.session_state.run_query:
        input_genes = st.session_state.input_genes

        if input_genes:
            gene_selection = map_gene_selection()
            selected_species = st.session_state.species
            input_genes = parse_multi_input(input_genes)

            annotation_data = []
            matched_input = set()
            missing_input = set()
            if st.session_state.gene_input_type == "Gene_ID":
                annotation_data = database.get_gene_annotation_data(input_genes, "xerophyta_gene_name",selected_species)
            
                if annotation_data:
                    matched_input = {gene.gene_name.lower() for gene in annotation_data}
                else:
                    matched_input = set()
                missing_input = {gene for gene in input_genes if gene.lower() not in matched_input}


            elif st.session_state.gene_input_type == "Arab_loci":
                annotation_data = database.get_gene_annotation_data(input_genes, "a_thaliana_locus",selected_species)
            
                if annotation_data:
                    matched_input = {gene.arabidopsis_homologues[0].a_thaliana_locus.lower() for gene in annotation_data}
                
                else:
                    matched_input = set()
                
                missing_input = {gene for gene in input_genes if gene.lower() not in matched_input}


            elif st.session_state.gene_input_type == "Arab_common_name":
                annotation_data = database.get_gene_annotation_data(input_genes, "a_thaliana_common_name",selected_species)

                if annotation_data:
                    # Determine which search terms did not match any homologues
                    for gene in annotation_data:
                        for homologue in gene.arabidopsis_homologues:
                            common_name = homologue.a_thaliana_common_name.lower()
                            for term in input_genes:
                                if term.lower() in common_name:
                                    matched_input.add(term)

                    missing_input = [term for term in input_genes if term not in matched_input]

            elif st.session_state.gene_input_type == "GO_term":
                # TODO
                annotation_data = []

            

            results= database.flatten_gene_annotation_data(annotation_data)
            df = pd.DataFrame(results)


            st.subheader("Search Results")
            st.write(f"Found {len(results)} gene(s).")
            if missing_input:
                st.warning(f"Input genes not found: {", ".join([i for i in missing_input])}")
            selected_columns = st.session_state.selected_columns

            if not df.empty:
                df['e value'] = df['e value'].astype(float)
                df.style.format({'e value': '{:.2e}'})
                st.dataframe(df[selected_columns],use_container_width=True)        

            

            #-------------------------
            # DOWNLOAD BUTTONS
            #-------------------------
            col1, col2 = st.columns(2)
            
            # DOWNLOAD GENE DATA BUTTON
            if not df.empty:
                csv_data = df[selected_columns].to_csv(index=False)
            else:
                csv_data = "No data was retrieved from the database. Please double-check your input."
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"Xerophyta_gene_query_results_{timestamp_str}.csv"
            
            with col1:
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv"
                )

            # DOWNLOAD FASTA BUTTON
            fasta_entries = []
            for gene in results:
                seq = gene["coding_sequence"] or ""
                
                # FASTA header: >GeneName description
                header = f">{gene["gene_name"]} {gene['description']}"

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
            2. Query Xerophyta gene ID  e.g Xele.ptg000049l.138, Xele.ptg000049l.140, Xele.ptg000049l.52
                or arabidopsis homologue (common name or locus ID)
            3. Query GO ID or GO name, Enzyme code or name, or InterPro ID
        """
    )


main()


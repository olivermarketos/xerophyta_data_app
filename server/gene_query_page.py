import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from utils.constants import GENE_SELECTION_OPTIONS
from utils.helper_functions import parse_input, retreive_query_data

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
                value=config["value"],
                key="input_genes",
                # value = st.session_state.input_genes,
                on_change=lambda: st.session_state.update({"input_genes": st.session_state.input_genes})  # Update session state on change
            )
            st.session_state.gene_input_type = config["key"]

    st.sidebar.multiselect(
        "Select columns to display:", ALL_COLUMNS, 
        default=ALL_COLUMNS,
        key="selected_columns")




def main():
    initialise_session_state()

    if st.sidebar.button("Run Query"):
        st.session_state.run_query = True
    
    if st.sidebar.button("Show Instructions") or not st.session_state.run_query:
        show_instructions()
        st.session_state.run_query = False

    setup_sidebar()

    if st.session_state.run_query:
        input_genes = st.session_state.input_genes

        if input_genes:
            selected_species = st.session_state.species
            input_genes = parse_input(input_genes)

            annotation_data, matched_input, missing_input = retreive_query_data(input_genes, selected_species, st.session_state.gene_input_type)

            results= database.flatten_gene_annotation_data(annotation_data)
            df = pd.DataFrame(results)


            st.subheader("Search Results")
            st.write(f"Found {len(results)} gene(s).")
            if missing_input:
                st.warning(f"Input genes not found: {', '.join([i for i in missing_input])}")
            selected_columns = st.session_state.selected_columns

            if not df.empty:
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
                header = f">{gene['gene_name']} {gene['description']}"

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


def show_instructions():

    # Welcome and brief introduction
    # Detailed steps and descriptions
    st.markdown(
        """
        ### Retrieve gene annotation information.

        The panel on the left provides various means to query the database to retreive gene annotation information.


        You can query the database using the following methods:

        1. **Filter by Xeropyhta species:**
            - Select a species from the dropdown menu to filter the results by species.

        2. **Query Xerophyta gene ID:**
            - Enter one or more Xerophyta gene IDs, separated by commas or newlines.
            - e.g. Xele.ptg000049l.138, Xele.ptg000049l.140, Xele.ptg000049l.52
            
        3. **Query Arabidopsis homologue locus id:**
            - Enter one or more Arabidopsis locus IDs, separated by commas or newlines.
            - e.g. At5g65540, At5g58510
            > __note__: search terms are case-insensitive

        4. **Arabidopsis homologue common name:**
            - Enter one or more Arabidopsis common names, separated by commas or newlines.
            - e.g expansin A4, auxin response factor 2
            > __note__: search terms are case-insensitive and partial matches are allowed
        
        5. **Query by GO id:**
            - Enter one or more GO terms, separated by commas or newlines.
            - The terms can be with or without a GO branch prefix (e.g. C:GO:0001939 or GO:0001939 will both work).
            - All genes returned will have at least one annotation with a matching GO term.

        6. **Query by GO name:**
            - Enter one or more GO term descriptions, separated by commas or newlines.
            - e.g. immune system process, leaf senescence
            - All genes returned will have at least one annotation with a matching GO term.
            > __note__: search terms are case-insensitive and partial matches are allowed and large queries may take longer to process.
                    
        7. **Query by Enzyme Code:**
            - Enter one or more enzyme codes, separated by commas or newlines.
            - e.g. EC:1.15.1.1, EC:1.2.3.4
            - All genes returned will have at least one annotation with a matching enzyme code.

        8. **Query by Enzyme Name:**
            - Enter one or more enzyme names, separated by commas or newlines.
            - e.g. NAD(+) glycohydrolase, oxalate oxidase
            - All genes returned will have at least one annotation with a matching enzyme name.
            > __note__: search terms are case-insensitive, partial matches are allowed and large queries may take longer to process.

        8. **Run Query:**
            - Click the "Run Query" button to retrieve the gene annotation information based on the input provided.
        
        9. **Download Results:**
            - After running the query, you can download the results as a CSV file or a FASTA file. 
        """
    )


main()
st.divider()
st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")




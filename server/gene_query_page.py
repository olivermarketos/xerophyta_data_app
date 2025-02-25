import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from utils.constants import GENE_ANNOTATION_SELECTION_OPTIONS
from utils.helper_functions import parse_input

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
    selected_gene_selection = st.sidebar.radio("Gene selection method:", list(GENE_ANNOTATION_SELECTION_OPTIONS.keys()), key="gene_selection")
    # Gene input field based on selection
    for option, config in GENE_ANNOTATION_SELECTION_OPTIONS.items():
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


def map_gene_selection():
    """
    Maps the gene selection method to the appropriate function.
    """
    gene_selection = {
        "Xerophyta GeneID": "xerophyta",
        "Arabidopsis homologue locus": "a_thaliana_locus",
        "Arabidopsis homologue common name": "a_thaliana_common_name",
        "Genes with GO id": "go_id",
        "Genes with GO name": "go_name",
        "Genes with Enzyme Code": "enzyme_code"
    }
    return gene_selection[st.session_state.gene_selection]




def main():
    initialise_session_state()
    setup_sidebar()
    if st.sidebar.button("Run Query"):
        st.session_state.run_query = True
    
    if st.sidebar.button("Show Instructions") or not st.session_state.run_query:
        instruction_page()
        st.session_state.run_query = False

    if st.session_state.run_query:
        input_genes = st.session_state.input_genes

        if input_genes:
            gene_selection = map_gene_selection()
            selected_species = st.session_state.species
            input_genes = parse_input(input_genes)

            annotation_data = []
            matched_input = set()
            missing_input = set()
            if st.session_state.gene_input_type == "Gene_ID":
                annotation_data = database.get_gene_annotation_data(input_genes, "xerophyta_gene_name",selected_species)
            
                if annotation_data:
                    matched_input = {gene.gene_name.lower() for gene in annotation_data}
                    st.write(f"matched input: {matched_input}")
                else:
                    matched_input = set()
                missing_input = {gene for gene in input_genes if gene.lower() not in matched_input}
                st.write(f"missing input {missing_input}")

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

            elif st.session_state.gene_input_type == "GO_id":
                annotation_data = database.get_gene_annotation_data(input_genes, "go_id",selected_species)
                
                normalized_inputs = {database.normalize_go_term(term) for term in input_genes}

                if annotation_data:
                    for gene in annotation_data:
                        for annotation in gene.annotations:
                            for go in annotation.go_ids:
                                normalized_go = database.normalize_go_term(go.go_id)
                                # Check for partial match: if either string contains the other.
                                # print(f'normalized_go: {normalized_go}')
                                for user_term in normalized_inputs:
                                    if user_term in normalized_go:
                                        matched_input.add(normalized_go)

                else:
                    matched_input = set()
                missing_input = normalized_inputs - matched_input
 
            elif st.session_state.gene_input_type == "GO_name":
                annotation_data = database.get_gene_annotation_data(input_genes, "go_name",selected_species)
                if annotation_data:
                    for gene in annotation_data:
                        for annotation in gene.annotations:
                            # iterate over GO objects via the go_ids relationship
                            for go in annotation.go_ids:
                                # Ensure go.go_name exists and normalize it to lowercase
                                go_name = go.go_name.lower() if go.go_name else ""
                                for term in input_genes:
                                    # Check if the lowercase search term is in the GO name
                                    if term.lower() in go_name:
                                        matched_input.add(term)
                    missing_input = [term for term in input_genes if term.lower() not in {m.lower() for m in matched_input}]

            elif st.session_state.gene_input_type == "EC_code":
                annotation_data = database.get_gene_annotation_data(input_genes, "enzyme_code",selected_species)
                
                matched_input = set()
                normalized_inputs = {term for term in input_genes}
                if annotation_data:
                    for gene in annotation_data:
                        for annotation in gene.annotations:
                            for enzyme_code in annotation.enzyme_codes:
                                for user_term in input_genes:
                                    if user_term in enzyme_code.enzyme_code:
                                        matched_input.add(enzyme_code.enzyme_code)
                                

                else:
                    matched_input = set()
                missing_input = normalized_inputs - matched_input


            results= database.flatten_gene_annotation_data(annotation_data)
            df = pd.DataFrame(results)


            st.subheader("Search Results")
            st.write(f"Found {len(results)} gene(s).")
            if missing_input:
                st.warning(f"Input genes not found: {", ".join([i for i in missing_input])}")
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
                    
        8. **Run Query:**
            - Click the "Run Query" button to retrieve the gene annotation information based on the input provided.
        
        9. **Download Results:**
            - After running the query, you can download the results as a CSV file or a FASTA file. 
        """
    )


main()


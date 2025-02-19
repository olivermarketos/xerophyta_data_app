import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from database.models import (
    Base, Species, Gene, Annotation, GO,
    EnzymeCode, InterPro, ArabidopsisHomologue
)

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

def build_combined_table(genes):
    """
    Takes a list of Gene objects (with joined relationships)
    and returns a DataFrame where each row corresponds to one Gene+Annotation combo,
    with columns for all relevant data (Gene, Annotation, GO, Enzyme, InterPro, etc.).
    """
    rows = []
    for g in genes:
        if not g.annotations:
            # No annotation => store minimal gene info
            rows.append({
                "Gene ID": g.id,
                "Gene Name": g.gene_name,
                "Species": g.species.name if g.species else None,
                "Annotation Description": None,
                "Annotation e-value": None,
                "Arab. Locus": g.arabidopsis_homologues.a_thaliana_locus ,
                "Arab. Common Name": g.arabidopsis_homologues.a_thaliana_common_name ,
                "GO Terms": None,
                "Enzyme Codes": None,
                "InterPro IDs": None,
            })
        else:
            for ann in g.annotations:
                go_list = [f"{go.go_id}({go.go_name})" for go in ann.go_ids]  
                enz_list = [f"{ec.enzyme_code}({ec.enzyme_name})" for ec in ann.enzyme_codes]
                ipr_list = [f"{ip.interpro_id}({ip.interpro_go_name})" for ip in ann.interpro_ids]

                row = {
                    "Gene ID": g.id,
                    "Gene Name": g.gene_name,
                    "Species": g.species.name if g.species else None,
                    "Annotation Description": ann.description,
                    "Annotation e-value": ann.e_value,
                     "Arab. Locus": g.arabidopsis_homologues.a_thaliana_locus ,
                    "Arab. Common Name": g.arabidopsis_homologues.a_thaliana_common_name ,
                    "GO Terms": "; ".join(go_list) if go_list else None,
                    "Enzyme Codes": "; ".join(enz_list) if enz_list else None,
                    "InterPro IDs": "; ".join(ipr_list) if ipr_list else None,
                }
                rows.append(row)

    df = pd.DataFrame(rows)
    df.drop_duplicates(inplace=True)
    return df


def main():
    st.title("Xerophyta Database Explorer")
    st.sidebar.header("Search Inputs")
    database = db.DB()

    # Species selection
    species_list = database.get_species()
    species_options = ["(Any)"] + [sp.name for sp in species_list]
    selected_species = st.sidebar.selectbox("Select Species (optional):", species_options)

    # Query inputs
    xero_gene_input = st.sidebar.text_area("Xerophyta Gene Names:")
    arab_gene_input = st.sidebar.text_area("Arabidopsis Genes/Loci:")
    advanced_input = st.sidebar.text_area("GO Terms, Enzyme Codes, InterPro IDs:")

    all_columns = [
            "Gene ID",
            "Gene Name",
            "Species",
            "Annotation Description",
            "Annotation e-value",
            "Arab. Locus",
            "Arab. Common Name",
            "GO Terms",
            "Enzyme Codes",
            "InterPro IDs"
        ]
    selected_columns = st.sidebar.multiselect(
        "Select columns to display:", all_columns, default=all_columns
    )

    if st.sidebar.button("Run Query"):
        xero_genes = parse_multi_input(xero_gene_input)
        arab_genes = parse_multi_input(arab_gene_input)
        adv_terms = parse_multi_input(advanced_input)

        results = database.query_genes_by_all(selected_species, xero_genes, arab_genes, adv_terms)
        df = build_combined_table(results)
        

        st.subheader("Search Results")
        st.write(f"Found {len(results)} gene(s).")
        st.dataframe(df[selected_columns], use_container_width=True)

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


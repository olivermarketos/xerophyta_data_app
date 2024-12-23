import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datetime import datetime 
import db as db  # Your custom db module
from models import (
    Base, Species, Gene, Annotation, GO,
    EnzymeCode, InterPro, ArabidopsisHomologue
)

def main():
    st.title("Xerophyta Database Explorer")
    instruction_page()
    # -------------------------
    # SIDEBAR
    # -------------------------
    st.sidebar.header("Search Inputs")
    database = db.DB()
    session = database.session

    # 1) Species Selection
    species_list = session.query(Species).all()
    species_options = ["(Any)"] + [sp.name for sp in species_list]
    selected_species = st.sidebar.selectbox(
        "Select Species (optional):",
        species_options
    )
    
    # 2) Xerophyta Gene Names
    st.sidebar.markdown("**Xerophyta Gene Names** (comma, space, or newline):")
    xero_gene_input = st.sidebar.text_area("e.g.: Xele.ptg000001l.1, Xele.ptg000001l.116,Xele.ptg000001l.16...")

    # 3) Arabidopsis Gene/Locus
    st.sidebar.markdown("**Arabidopsis Genes/Loci** (comma, space, or newline):")
    arab_gene_input = st.sidebar.text_area("e.g.: AT1G01010, AT1G01020")

    # 4) GO, Enzyme, InterPro
    st.sidebar.markdown("**GO Term(s) / Enzyme Code(s) / InterPro ID(s)** (comma, space, or newline):")
    advanced_input = st.sidebar.text_area("e.g.: GO:0008150, 1.1.1.1, IPR000123")

    # Multi-select for which columns to display
    st.sidebar.markdown("---")
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
        "Select columns to display in the results table:",
        all_columns,
        default=all_columns  # Show all by default
    )

    # -------------------------
    # QUERY BUTTON
    # -------------------------
    if st.sidebar.button("Run Query"):
        # Parse and clean up user inputs
        xero_genes = parse_multi_input(xero_gene_input)
        arab_genes = parse_multi_input(arab_gene_input)
        adv_terms  = parse_multi_input(advanced_input)

        # Build the query
        query = (
            session.query(Gene)
            # Either .outerjoin(Species) or .join(Species, isouter=True)
            .outerjoin(Species)  
            .outerjoin(Gene.annotations)
            .outerjoin(Annotation.go_ids)
            .outerjoin(Annotation.enzyme_codes)
            .outerjoin(Annotation.interpro_ids)
            .outerjoin(Gene.arabidopsis_homologues)
            .distinct()
        )

        # (A) Filter by species if chosen
        if selected_species != "(Any)":
            query = query.filter(Species.name == selected_species)

        # (B) Filter by Xerophyta gene name(s)
        if xero_genes:
            query = query.filter(
                or_(*[Gene.gene_name.ilike(f"{g}") for g in xero_genes])
            )
 

        # (C) Filter by Arabidopsis gene/locus
        if arab_genes:
            query = query.filter(
                or_(
                    *[
                        ArabidopsisHomologue.a_thaliana_locus.ilike(f"%{a}%")
                        for a in arab_genes
                    ],
                    *[
                        ArabidopsisHomologue.a_thaliana_common_name.ilike(f"%{a}%")
                        for a in arab_genes
                    ]
                )
            )

        # (D) Filter by GO terms, Enzyme codes, InterPro IDs
        if adv_terms:
            query = query.filter(
                or_(
                    *[
                        GO.go_id.ilike(f"%{t}%") |
                        GO.go_name.ilike(f"%{t}%") |
                        EnzymeCode.enzyme_code.ilike(f"%{t}%") |
                        EnzymeCode.enzyme_name.ilike(f"%{t}%") |
                        InterPro.interpro_id.ilike(f"%{t}%") |
                        InterPro.interpro_go_name.ilike(f"%{t}%")
                        for t in adv_terms
                    ]
                )
            )

        # Execute
        results = query.all()

        # Build a combined table for the results
        df = build_combined_table(results)
        
        # If user only wants some columns, filter them
        df_filtered = df[selected_columns]

        st.subheader("Search Results")
        st.write(f"Found {len(results)} gene(s).")
        st.dataframe(df_filtered, use_container_width=True)

        #-------------------------
        # DOWNLOAD BUTTONS
        #-------------------------
        col1, col2 = st.columns(2)
        
        # Download gene data button
        csv_data = df_filtered.to_csv(index=False)
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



    # Cleanup
    session.close()


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
                "Arab. Locus": combine_homologues_locus(g.arabidopsis_homologues),
                "Arab. Common Name": combine_homologues_common(g.arabidopsis_homologues),
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
                    "Arab. Locus": combine_homologues_locus(g.arabidopsis_homologues),
                    "Arab. Common Name": combine_homologues_common(g.arabidopsis_homologues),
                    "GO Terms": "; ".join(go_list) if go_list else None,
                    "Enzyme Codes": "; ".join(enz_list) if enz_list else None,
                    "InterPro IDs": "; ".join(ipr_list) if ipr_list else None,
                }
                rows.append(row)

    df = pd.DataFrame(rows)
    df.drop_duplicates(inplace=True)
    return df


def combine_homologues_locus(homologues):
    """Joins all Arabidopsis homologue locus IDs into a single string."""
    if not homologues:
        return None
    return ", ".join([h.a_thaliana_locus for h in homologues if h.a_thaliana_locus])


def combine_homologues_common(homologues):
    """Joins all Arabidopsis homologue common names into a single string."""
    if not homologues:
        return None
    return ", ".join(
        [h.a_thaliana_common_name for h in homologues if h.a_thaliana_common_name]
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


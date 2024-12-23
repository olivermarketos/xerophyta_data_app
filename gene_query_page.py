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


# st.title("Simple Database Explorer")

# # --------------------------------------------------------------------------
# # Helper function to convert Gene objects to a DataFrame
# # --------------------------------------------------------------------------
# def convert_genes_to_df(genes):
#     """
#     Convert a list of Gene objects into a pandas DataFrame with some basic info.
#     You can add/remove fields as you see fit.
#     """
#     data = []
#     for g in genes:
#         data.append({
#             "Gene ID": g.id,
#             "Gene Name": g.gene_name,
#             "Species": g.species.name if g.species else "N/A",
#             # You could add more columns here, e.g., coding sequence, etc.
#         })
#     df = pd.DataFrame(data)
#     return df


# # --------------------------------------------------------------------------
# # 2. Species Picker (Sidebar)
# # --------------------------------------------------------------------------
# st.sidebar.header("Species Selector")
# species_list = database.session.query(Species).all()

# if species_list:
#     species_names = [sp.name for sp in species_list]
#     selected_species_name = st.sidebar.selectbox(
#         "Select a species:",
#         species_names
#     )

#     selected_species = (
#         database.session.query(Species)
#         .filter(Species.name == selected_species_name)
#         .first()
#     )
# else:
#     st.write("No species found in database.")
#     st.stop()

# st.markdown("---")

# # --------------------------------------------------------------------------
# # 3. Standard Gene Search (by name)
# # --------------------------------------------------------------------------
# st.subheader("Search for a gene by name:")
# search_input = st.text_input("Enter part (or all) of a gene name")

# if search_input:
#     results = (
#         database.session.query(Gene)
#         .filter(Gene.gene_name.ilike(f"%{search_input}%"))
#         .all()
#     )
#     if results:
#         st.write(f"Found {len(results)} gene(s) matching '{search_input}':")
        
#         # Convert to DataFrame
#         df_results = convert_genes_to_df(results)
#         st.dataframe(df_results)
        
#         # Download button
#         csv_data = df_results.to_csv(index=False)
#         st.download_button(
#             label="Download search results as CSV",
#             data=csv_data,
#             file_name="gene_search_results.csv",
#             mime="text/csv"
#         )
#     else:
#         st.write(f"No genes match '{search_input}'")

# st.markdown("---")

# # --------------------------------------------------------------------------
# # 4. ADVANCED SEARCH
# # --------------------------------------------------------------------------
# st.subheader("Advanced Search")

# search_type = st.selectbox(
#     "Search by:",
#     [
#         "Arabidopsis Locus",
#         "Arabidopsis Common Name",
#         "GO Term or ID",
#         "Enzyme Code",
#         "InterPro ID"
#     ]
# )

# adv_search_input = st.text_input("Enter your search term/value here")

# if st.button("Search Advanced"):
#     if not adv_search_input.strip():
#         st.warning("Please enter a search term.")
#     else:
#         results = []
#         if search_type == "Arabidopsis Locus":
#             results = (
#                 database.session.query(Gene)
#                 .join(Gene.arabidopsis_homologues)
#                 .filter(ArabidopsisHomologue.a_thaliana_locus.ilike(f"%{adv_search_input}%"))
#                 .all()
#             )
#         elif search_type == "Arabidopsis Common Name":
#             results = (
#                 database.session.query(Gene)
#                 .join(Gene.arabidopsis_homologues)
#                 .filter(ArabidopsisHomologue.a_thaliana_common_name.ilike(f"%{adv_search_input}%"))
#                 .all()
#             )
#         elif search_type == "GO Term or ID":
#             results = (
#                 database.session.query(Gene)
#                 .join(Gene.annotations)
#                 .join(Annotation.go_ids)
#                 .filter(
#                     (GO.go_id.ilike(f"%{adv_search_input}%"))
#                     | (GO.go_name.ilike(f"%{adv_search_input}%"))
#                 )
#                 .all()
#             )
#         elif search_type == "Enzyme Code":
#             results = (
#                 database.session.query(Gene)
#                 .join(Gene.annotations)
#                 .join(Annotation.enzyme_codes)
#                 .filter(
#                     (EnzymeCode.enzyme_code.ilike(f"%{adv_search_input}%"))
#                     | (EnzymeCode.enzyme_name.ilike(f"%{adv_search_input}%"))
#                 )
#                 .all()
#             )
#         elif search_type == "InterPro ID":
#             results = (
#                 database.session.query(Gene)
#                 .join(Gene.annotations)
#                 .join(Annotation.interpro_ids)
#                 .filter(
#                     (InterPro.interpro_id.ilike(f"%{adv_search_input}%"))
#                     | (InterPro.interpro_go_name.ilike(f"%{adv_search_input}%"))
#                 )
#                 .all()
#             )

#         if results:
#             st.write(
#                 f"Found {len(results)} Gene(s) matching **'{adv_search_input}'** "
#                 f"in **'{search_type}'**:"
#             )
#             # Convert to DataFrame
#             df_results = convert_genes_to_df(results)
#             st.dataframe(df_results)

#             # Download button
#             csv_data = df_results.to_csv(index=False)
#             st.download_button(
#                 label="Download advanced search results as CSV",
#                 data=csv_data,
#                 file_name="advanced_search_results.csv",
#                 mime="text/csv"
#             )
#         else:
#             st.write(f"No genes found for '{adv_search_input}' in {search_type}.")

# st.markdown("---")

# # --------------------------------------------------------------------------
# # 5. Gene Details & Annotations
# # --------------------------------------------------------------------------
# st.subheader("View Gene Details & Annotations")

# all_genes = database.session.query(Gene).all()
# if all_genes:
#     gene_options = [f"{g.gene_name} (ID={g.id})" for g in all_genes]
#     gene_selected = st.selectbox("Select a gene:", gene_options)
    
#     # Parse the ID out of the selectbox string (assuming "name (ID=X)")
#     gene_id = int(gene_selected.split("ID=")[1].replace(")", ""))
#     selected_gene = database.session.query(Gene).filter_by(id=gene_id).first()

#     if selected_gene:
#         st.write("**Gene Name:**", selected_gene.gene_name)
#         st.write("**Species:**", selected_gene.species.name)
#         st.write("**Coding Sequence:**", selected_gene.coding_sequence)
        
#         # Show Annotations
#         annotations = selected_gene.annotations
#         if annotations:
#             st.write("### Annotations")
#             # We'll build a small table of annotation details
#             ann_data = []
#             for ann in annotations:
#                 # Collect basic annotation fields
#                 ann_record = {
#                     "Annotation ID": ann.id,
#                     "Description": ann.description,
#                     "e-value": ann.e_value
#                 }
#                 ann_data.append(ann_record)
            
#             # Convert annotation data to a DataFrame
#             df_ann = pd.DataFrame(ann_data)
#             st.dataframe(df_ann)

#             # Download button for annotation data
#             csv_ann = df_ann.to_csv(index=False)
#             st.download_button(
#                 label="Download annotations as CSV",
#                 data=csv_ann,
#                 file_name=f"gene_{selected_gene.id}_annotations.csv",
#                 mime="text/csv"
#             )

#             st.markdown("#### Linked GO Terms")
#             # Combine all GO terms from all annotations into a single list
#             go_list = []
#             for ann in annotations:
#                 for go_term in ann.go_ids:
#                     go_list.append({
#                         "GO ID": go_term.go_id,
#                         "GO Name": go_term.go_name,
#                         "GO Branch": go_term.go_branch
#                     })
#             if go_list:
#                 df_go = pd.DataFrame(go_list)
#                 st.dataframe(df_go.drop_duplicates())
#                 csv_go = df_go.drop_duplicates().to_csv(index=False)
#                 st.download_button(
#                     label="Download GO terms as CSV",
#                     data=csv_go,
#                     file_name=f"gene_{selected_gene.id}_go_terms.csv",
#                     mime="text/csv"
#                 )
#             else:
#                 st.write("No GO terms linked.")

#             st.markdown("#### Linked Enzyme Codes")
#             enz_list = []
#             for ann in annotations:
#                 for enz in ann.enzyme_codes:
#                     enz_list.append({
#                         "Enzyme Code": enz.enzyme_code,
#                         "Enzyme Name": enz.enzyme_name
#                     })
#             if enz_list:
#                 df_enz = pd.DataFrame(enz_list)
#                 st.dataframe(df_enz.drop_duplicates())
#                 csv_enz = df_enz.drop_duplicates().to_csv(index=False)
#                 st.download_button(
#                     label="Download Enzyme codes as CSV",
#                     data=csv_enz,
#                     file_name=f"gene_{selected_gene.id}_enzyme_codes.csv",
#                     mime="text/csv"
#                 )
#             else:
#                 st.write("No enzyme codes linked.")

#             st.markdown("#### Linked InterPro IDs")
#             ipr_list = []
#             for ann in annotations:
#                 for ipr in ann.interpro_ids:
#                     ipr_list.append({
#                         "InterPro ID": ipr.interpro_id,
#                         "InterPro GO Name": ipr.interpro_go_name
#                     })
#             if ipr_list:
#                 df_ipr = pd.DataFrame(ipr_list)
#                 st.dataframe(df_ipr.drop_duplicates())
#                 csv_ipr = df_ipr.drop_duplicates().to_csv(index=False)
#                 st.download_button(
#                     label="Download InterPro as CSV",
#                     data=csv_ipr,
#                     file_name=f"gene_{selected_gene.id}_interpro_ids.csv",
#                     mime="text/csv"
#                 )
#             else:
#                 st.write("No InterPro IDs linked.")

#         else:
#             st.write("No annotations found for this gene.")
# else:
#     st.write("No genes in the database.")

# # Close the session
# database.session.close()

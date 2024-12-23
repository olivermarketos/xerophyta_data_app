# streamlit_app.py

import streamlit as st
import pandas as pd  # <-- NEW: for tables and CSV download
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import db as db  # Your custom db module
# Import your models
from models import (
    Base, Species, Gene, Annotation, GO,
    EnzymeCode, InterPro, ArabidopsisHomologue
)

# --------------------------------------------------------------------------
# 1. CREATE DATABASE ENGINE AND SESSION
# --------------------------------------------------------------------------
database = db.DB()

# Base.metadata.create_all(bind=database.engine)  # Uncomment if you need to create tables

st.title("Simple Database Explorer")

# --------------------------------------------------------------------------
# Helper function to convert Gene objects to a DataFrame
# --------------------------------------------------------------------------
def convert_genes_to_df(genes):
    """
    Convert a list of Gene objects into a pandas DataFrame with some basic info.
    You can add/remove fields as you see fit.
    """
    data = []
    for g in genes:
        data.append({
            "Gene ID": g.id,
            "Gene Name": g.gene_name,
            "Species": g.species.name if g.species else "N/A",
            # You could add more columns here, e.g., coding sequence, etc.
        })
    df = pd.DataFrame(data)
    return df


# --------------------------------------------------------------------------
# 2. Species Picker (Sidebar)
# --------------------------------------------------------------------------
st.sidebar.header("Species Selector")
species_list = database.session.query(Species).all()

if species_list:
    species_names = [sp.name for sp in species_list]
    selected_species_name = st.sidebar.selectbox(
        "Select a species:",
        species_names
    )

    selected_species = (
        database.session.query(Species)
        .filter(Species.name == selected_species_name)
        .first()
    )
else:
    st.write("No species found in database.")
    st.stop()

st.markdown("---")

# --------------------------------------------------------------------------
# 3. Standard Gene Search (by name)
# --------------------------------------------------------------------------
st.subheader("Search for a gene by name:")
search_input = st.text_input("Enter part (or all) of a gene name")

if search_input:
    results = (
        database.session.query(Gene)
        .filter(Gene.gene_name.ilike(f"%{search_input}%"))
        .all()
    )
    if results:
        st.write(f"Found {len(results)} gene(s) matching '{search_input}':")
        
        # Convert to DataFrame
        df_results = convert_genes_to_df(results)
        st.dataframe(df_results)
        
        # Download button
        csv_data = df_results.to_csv(index=False)
        st.download_button(
            label="Download search results as CSV",
            data=csv_data,
            file_name="gene_search_results.csv",
            mime="text/csv"
        )
    else:
        st.write(f"No genes match '{search_input}'")

st.markdown("---")

# --------------------------------------------------------------------------
# 4. ADVANCED SEARCH
# --------------------------------------------------------------------------
st.subheader("Advanced Search")

search_type = st.selectbox(
    "Search by:",
    [
        "Arabidopsis Locus",
        "Arabidopsis Common Name",
        "GO Term or ID",
        "Enzyme Code",
        "InterPro ID"
    ]
)

adv_search_input = st.text_input("Enter your search term/value here")

if st.button("Search Advanced"):
    if not adv_search_input.strip():
        st.warning("Please enter a search term.")
    else:
        results = []
        if search_type == "Arabidopsis Locus":
            results = (
                database.session.query(Gene)
                .join(Gene.arabidopsis_homologues)
                .filter(ArabidopsisHomologue.a_thaliana_locus.ilike(f"%{adv_search_input}%"))
                .all()
            )
        elif search_type == "Arabidopsis Common Name":
            results = (
                database.session.query(Gene)
                .join(Gene.arabidopsis_homologues)
                .filter(ArabidopsisHomologue.a_thaliana_common_name.ilike(f"%{adv_search_input}%"))
                .all()
            )
        elif search_type == "GO Term or ID":
            results = (
                database.session.query(Gene)
                .join(Gene.annotations)
                .join(Annotation.go_ids)
                .filter(
                    (GO.go_id.ilike(f"%{adv_search_input}%"))
                    | (GO.go_name.ilike(f"%{adv_search_input}%"))
                )
                .all()
            )
        elif search_type == "Enzyme Code":
            results = (
                database.session.query(Gene)
                .join(Gene.annotations)
                .join(Annotation.enzyme_codes)
                .filter(
                    (EnzymeCode.enzyme_code.ilike(f"%{adv_search_input}%"))
                    | (EnzymeCode.enzyme_name.ilike(f"%{adv_search_input}%"))
                )
                .all()
            )
        elif search_type == "InterPro ID":
            results = (
                database.session.query(Gene)
                .join(Gene.annotations)
                .join(Annotation.interpro_ids)
                .filter(
                    (InterPro.interpro_id.ilike(f"%{adv_search_input}%"))
                    | (InterPro.interpro_go_name.ilike(f"%{adv_search_input}%"))
                )
                .all()
            )

        if results:
            st.write(
                f"Found {len(results)} Gene(s) matching **'{adv_search_input}'** "
                f"in **'{search_type}'**:"
            )
            # Convert to DataFrame
            df_results = convert_genes_to_df(results)
            st.dataframe(df_results)

            # Download button
            csv_data = df_results.to_csv(index=False)
            st.download_button(
                label="Download advanced search results as CSV",
                data=csv_data,
                file_name="advanced_search_results.csv",
                mime="text/csv"
            )
        else:
            st.write(f"No genes found for '{adv_search_input}' in {search_type}.")

st.markdown("---")

# --------------------------------------------------------------------------
# 5. Gene Details & Annotations
# --------------------------------------------------------------------------
st.subheader("View Gene Details & Annotations")

all_genes = database.session.query(Gene).all()
if all_genes:
    gene_options = [f"{g.gene_name} (ID={g.id})" for g in all_genes]
    gene_selected = st.selectbox("Select a gene:", gene_options)
    
    # Parse the ID out of the selectbox string (assuming "name (ID=X)")
    gene_id = int(gene_selected.split("ID=")[1].replace(")", ""))
    selected_gene = database.session.query(Gene).filter_by(id=gene_id).first()

    if selected_gene:
        st.write("**Gene Name:**", selected_gene.gene_name)
        st.write("**Species:**", selected_gene.species.name)
        st.write("**Coding Sequence:**", selected_gene.coding_sequence)
        
        # Show Annotations
        annotations = selected_gene.annotations
        if annotations:
            st.write("### Annotations")
            # We'll build a small table of annotation details
            ann_data = []
            for ann in annotations:
                # Collect basic annotation fields
                ann_record = {
                    "Annotation ID": ann.id,
                    "Description": ann.description,
                    "e-value": ann.e_value
                }
                ann_data.append(ann_record)
            
            # Convert annotation data to a DataFrame
            df_ann = pd.DataFrame(ann_data)
            st.dataframe(df_ann)

            # Download button for annotation data
            csv_ann = df_ann.to_csv(index=False)
            st.download_button(
                label="Download annotations as CSV",
                data=csv_ann,
                file_name=f"gene_{selected_gene.id}_annotations.csv",
                mime="text/csv"
            )

            st.markdown("#### Linked GO Terms")
            # Combine all GO terms from all annotations into a single list
            go_list = []
            for ann in annotations:
                for go_term in ann.go_ids:
                    go_list.append({
                        "GO ID": go_term.go_id,
                        "GO Name": go_term.go_name,
                        "GO Branch": go_term.go_branch
                    })
            if go_list:
                df_go = pd.DataFrame(go_list)
                st.dataframe(df_go.drop_duplicates())
                csv_go = df_go.drop_duplicates().to_csv(index=False)
                st.download_button(
                    label="Download GO terms as CSV",
                    data=csv_go,
                    file_name=f"gene_{selected_gene.id}_go_terms.csv",
                    mime="text/csv"
                )
            else:
                st.write("No GO terms linked.")

            st.markdown("#### Linked Enzyme Codes")
            enz_list = []
            for ann in annotations:
                for enz in ann.enzyme_codes:
                    enz_list.append({
                        "Enzyme Code": enz.enzyme_code,
                        "Enzyme Name": enz.enzyme_name
                    })
            if enz_list:
                df_enz = pd.DataFrame(enz_list)
                st.dataframe(df_enz.drop_duplicates())
                csv_enz = df_enz.drop_duplicates().to_csv(index=False)
                st.download_button(
                    label="Download Enzyme codes as CSV",
                    data=csv_enz,
                    file_name=f"gene_{selected_gene.id}_enzyme_codes.csv",
                    mime="text/csv"
                )
            else:
                st.write("No enzyme codes linked.")

            st.markdown("#### Linked InterPro IDs")
            ipr_list = []
            for ann in annotations:
                for ipr in ann.interpro_ids:
                    ipr_list.append({
                        "InterPro ID": ipr.interpro_id,
                        "InterPro GO Name": ipr.interpro_go_name
                    })
            if ipr_list:
                df_ipr = pd.DataFrame(ipr_list)
                st.dataframe(df_ipr.drop_duplicates())
                csv_ipr = df_ipr.drop_duplicates().to_csv(index=False)
                st.download_button(
                    label="Download InterPro as CSV",
                    data=csv_ipr,
                    file_name=f"gene_{selected_gene.id}_interpro_ids.csv",
                    mime="text/csv"
                )
            else:
                st.write("No InterPro IDs linked.")

        else:
            st.write("No annotations found for this gene.")
else:
    st.write("No genes in the database.")

# Close the session
database.session.close()

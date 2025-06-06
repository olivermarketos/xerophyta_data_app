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
    
@st.cache_data
def get_gene_names():
    all_gene_objects = database.get_gene_names_from_species("X. elegans")
    all_gene_names = [g.gene_name for g in all_gene_objects]
    return all_gene_names

def setup_sidebar():
    st.sidebar.header("Filter Options")

    # TODO change this to be dynamic once there is GRN data for other species
    selected_species = st.sidebar.selectbox(
        "Filter by Species (for interacting genes):",
        options="X. elegans",
        index=0,
        help="Select a species. Currently only Xerophyta elegans is available.",
        key="species_filter"
    )


    all_gene_names = get_gene_names()
    all_gene_names = ["None"] + all_gene_names
    regulator_gene_query = st.sidebar.selectbox(
        "Query gene",
            all_gene_names,
            index=0,
            key="query_gene",
            placeholder="Select a regulator gene name or enter one",
            accept_new_options=True,
            help="Enter full gene name for the regulator. Leave as None to query all genes."

        )

    target_gene_query = st.sidebar.selectbox(
        "Target Gene Name",
        all_gene_names,
        index=0,
        key="target_gene",
        placeholder="Select a target gene name or enter one",
        accept_new_options=True,
        help="Enter full or partial gene name for the target. Leave as None to query all genes."
    )
    # regulatory_cluster_query = st.sidebar.text_input(
    #     "Regulatory Cluster (contains):",
    #     help="Enter full or partial regulatory cluster name."
    # )
    # target_cluster_query = st.sidebar.text_input(
    #     "Target Cluster (contains):",
    #     help="Enter full or partial target cluster name."
    # )
    # selected_directions = st.sidebar.multiselect(
    #     "Direction of Regulation:",
    #     options=direction_options,
    #     default=[],
    #     help="Select one or more directions of regulation."
    # )
    
    limit_results = st.sidebar.number_input(
        "Max Results to Display:",
        min_value=10,
        max_value=5000,
        value=100,
        step=50
    )




def main():
    initialise_session_state()

    if st.sidebar.button("Run Query"):
        st.session_state.run_query = True
    
    if st.sidebar.button("Show Instructions") or not st.session_state.run_query:
        show_instructions()
        st.session_state.run_query = False

    setup_sidebar()

    if st.session_state.run_query:
        query_gene = st.session_state.query_gene
        query = database.get_regulatory_interactions(query_gene)
        st.dataframe(query, use_container_width=True)
   
def show_instructions():

    # Welcome and brief introduction
    # Detailed steps and descriptions
    st.markdown(
        """
        ### Retrieve Gene Regulatory Network  information.

        The panel on the left provides various means to query the database to retreive gene annotation information.

        """
    )


main()
st.divider()
st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")




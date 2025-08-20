import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from utils.constants import GENE_SELECTION_OPTIONS
from utils.helper_functions import parse_input, retreive_query_data
from database.models import RegulatoryInteraction, Gene, Species



st.title("Xerophyta Database Explorer")
st.divider()
database = db.DB()


def initialise_session_state():
    if "run_query" not in st.session_state:
        st.session_state.run_query = False
    if "input_genes" not in st.session_state:
        st.session_state.input_genes = ""
    

@st.cache_data
def load_interaction_filters():
    return {
        'regulatory_cluster':    database.get_distinct_values(RegulatoryInteraction, 'regulatory_cluster'),
        'target_cluster':        database.get_distinct_values(RegulatoryInteraction, 'target_cluster'),
        'direction':             database.get_distinct_values(RegulatoryInteraction, 'direction'),
        'regulator_genes':       database.get_distinct_regulator_gene_names("X. elegans"),
        'target_genes':          database.get_distinct_target_gene_names("X. elegans"),
    }

def get_gene_names():
    all_gene_objects = database.get_gene_names_from_species("X. elegans")
    all_gene_names = [g.gene_name for g in all_gene_objects]
    return all_gene_names

def setup_sidebar():
    st.sidebar.header("Filter Options")

    filters = load_interaction_filters()

    # TODO change this to be dynamic once there is GRN data for other species
    selected_species = st.sidebar.selectbox(
        "Filter by Species (for interacting genes):",
        options="X. elegans",
        index=0,
        help="Select a species. Currently only Xerophyta elegans is available.",
        key="species_filter"
    )


    regulator_gene_query = st.sidebar.selectbox(
        "Query gene",
        ["Any"]+filters['regulator_genes'],
        index=0,
        key="query_gene",
        accept_new_options=True,
        help="Select a regulator gene from the GRN."
    )

    target_gene_query = st.sidebar.selectbox(
        "Target Gene Name",
        ["Any"] + filters['target_genes'],
        index=0,
        key="target_gene",
        accept_new_options=True,
        help="Select a target gene from the GRN."
    )    
    regulatory_cluster_query = st.sidebar.selectbox(
        "Regulatory Cluster:",
        ["Any"]+filters['regulatory_cluster'],
        help="Select or enter a gene cluster name. Leave as Any keep all clusters.",
        key="regulatory_cluster",
    )
    target_cluster_query = st.sidebar.selectbox(
        "Target Cluster:",
        ["Any"]+filters['target_cluster'],
        key="target_cluster",
        help="Select or enter a gene cluster name. Leave as Any keep all clusters."
    )
    selected_directions = st.sidebar.selectbox(
        "Direction of Regulation:",
        ["Any"]+filters['direction'],
        key="direction",
        help="Select one or more directions of regulation."
    )
    
    limit_results = st.sidebar.number_input(
        "Max Results to Display:",
        key="limit_results",
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
        filter_args = {
            "species_name": "X. elegans",
            "regulatory_cluster": st.session_state.regulatory_cluster if st.session_state.regulatory_cluster != "Any" else None,
            "target_cluster": st.session_state.target_cluster if st.session_state.target_cluster != "Any" else None,
            "directions": [st.session_state.direction] if st.session_state.direction != "Any" else None,
            "regulator_gene_name": st.session_state.query_gene if st.session_state.query_gene != "Any" else None,
            "target_gene_name": st.session_state.target_gene if st.session_state.target_gene != "Any" else None,

            "limit": st.session_state.limit_results
        }
        with st.spinner("Fetching GRN data..."):
            try:
                query = database.get_regulatory_interactions(**filter_args)

                if query:
                    interactions_df= pd.DataFrame(query)
                    st.subheader(f"Found {len(interactions_df)} Regulatory Interactions (displaying up to {st.session_state.limit_results}):")
                    st.dataframe(interactions_df, hide_index=True)

                    @st.cache_data # Cache the dataframe conversion for download
                    def convert_df_to_csv(df_to_convert):
                        return df_to_convert.to_csv(index=False).encode('utf-8')

                    csv_download = convert_df_to_csv(interactions_df)
                    st.download_button(
                        label="Download results as CSV",
                        data=csv_download,
                        file_name="grn_interactions_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No regulatory interactions found matching your criteria.")
            except Exception as e:
                st.error(f"An error occurred while fetching data: {e}")
                st.exception(e) # Shows the full traceback for debugging
        
   
def show_instructions():

    # Welcome and brief introduction
    # Detailed steps and descriptions
    st.markdown("""
    ### How to use the Xerophyta Gene Regulatory Network Explorer

    Use the controls on the left to filter and retrieve gene regulatory interactions.

    **1. Species**  
    - Currently only **X. elegans** is available.  

    **2. Regulator Gene**  
    - Select or enter a regulator gene which appears in the network, or leave as **Any** to include all.  

    **3. Target Gene**  
    - Select a target gene present in the GRN, or **Any** for all targets.  

    **4. Regulatory Cluster**  
    - Filter by upstream cluster (e.g. `HSF:1`), or **Any**. 
    - Use the dropdown to select one.
 

    **5. Target Cluster**  
    - Filter by downstream cluster (e.g. `HD-ZIP:1`), or **Any**.  
    - Use the dropdown to select one.


    **6. Direction of Regulation**  
    - Choose **Activation**, **Repression** or **Unknown**.  
    - Use the dropdown to select one

    **7. Max Results**  
    - Limit how many rows to display (default 100, up to 5000).

    **8. Run Query**  
    - Click **Run Query** to fetch.  
    - If matches are found, they appear in a table below.  

    **9. Download**  
    - Click **Download results as CSV** to save your filtered interactions.

    **Troubleshooting & Tips**  
    - If you see “No regulatory interactions found matching your criteria.”, try broadening filters (e.g. set clusters back to **Any**).  


    """)

main()
st.divider()
st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")




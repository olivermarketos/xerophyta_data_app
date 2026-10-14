import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import database.db as db
from utils.helper_functions import parse_input

# Get absolute paths for images to ensure they load on first app startup
SCRIPT_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = SCRIPT_DIR / "images"

# GRN figure and caption shown for each species
GRN_FIGURES = {
    "X. elegans": (
        "Fig5_grn.tiff",
        "Figure 5. Reconstruction of gene regulatory network using a consensus approach. (Reference paper?)",
    ),
    # TODO: caption from the biologist
    "X. schlechteri": (
        "x_schlechteri_grn.tiff",
        "Reconstruction of the X. schlechteri gene regulatory network.",
    ),
}

@st.cache_resource
def load_image(image_path):
    """Cache images to ensure they're registered in Streamlit's media handler on first load"""
    return Image.open(image_path)

@st.cache_data
def get_species_with_grn():
    return [species.name for species in database.get_species_with_grn()]

@st.cache_data
def get_tf_groups(species):
    return database.get_tf_groups(species)

@st.cache_data
def get_clusters(tf, species, verbose=False):
    # cluster names (e.g. "WRKY:1") are reused across species, so always filter by species
    return database.get_tf_group_targets(tf, species, verbose)

@st.cache_data
def get_gene_groups(genes, species):
    return database.get_gene_grn_clusters(genes, species)


st.title("Gene Regulatory Network")
st.divider()
database = db.DB()

selected_species = st.radio("Select a species:", get_species_with_grn(), key="grn_species", horizontal=True)

if selected_species in GRN_FIGURES:
    figure, caption = GRN_FIGURES[selected_species]
    st.image(load_image(IMAGE_DIR / figure), width=600)
    st.caption(caption)


clusters_tab, gene_info_tab = st.tabs(
    ['TF group info', 'Gene info']
)

with clusters_tab:
    st.markdown("""
        - Enter ID of a TF group from the above figure and the Data Explorer will list all the TG clusters predicted to be regulated.
        """)

    TFs = get_tf_groups(selected_species)
    verbose = st.checkbox("Show all genes in clusters (aggregated into lists for readability)")
    selected_tf = st.selectbox("Enter factor",TFs, index=None,label_visibility="hidden", placeholder="Select a transcription factor...")
    if selected_tf is not None:
        st.dataframe(get_clusters(selected_tf, selected_species, verbose))
        st.caption("💡 Tip: Data can be downloaded as CSV using button in top-right corner of the table")


with gene_info_tab:
    st.markdown(f"""
                - Enter _{selected_species}_ ID and retrieve all the TF and Target gene groups
                """)

    with st.form("gene_search_form"):
        selected_genes = parse_input(st.text_area(f"Enter {selected_species} gene IDs separated by space, comma or new line"))
        submit_button = st.form_submit_button("Search Genes")

    if submit_button and selected_genes:
        gene_groups = get_gene_groups(selected_genes, selected_species)

        # Transform results into a single DataFrame
        display_data = []
        for gene in gene_groups:
            display_data.append({
                "Gene ID": gene,
                "Regulatory Clusters": ", ".join(gene_groups[gene]['regulatory_clusters']) or "None",
                "Target Clusters": ", ".join(gene_groups[gene]['target_clusters']) or "None"
            })

        df = pd.DataFrame(display_data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.caption("💡 Tip: Data can be downloaded as CSV using button in top-right corner of the table")

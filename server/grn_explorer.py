import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  
from utils.constants import GENE_SELECTION_OPTIONS
from utils.helper_functions import parse_input, retreive_query_data
from database.models import RegulatoryInteraction, Gene, Species
from sqlalchemy.orm import aliased
from sqlalchemy import func

#TODO allow selecting more than one TF group at a time, loop over each group and agg results?

@st.cache_data
def get_clusters(tf, verbose=False):

    if verbose:
        RegulatorGene = aliased(Gene)
        TargetGene = aliased(Gene)

        query = (
            database.session.query(
                RegulatoryInteraction.regulatory_cluster,
                func.group_concat(RegulatorGene.gene_name.distinct()).label('regulator_genes'),
                RegulatoryInteraction.target_cluster,
                func.group_concat(TargetGene.gene_name.distinct()).label('target_genes'),
                RegulatoryInteraction.direction
            )
            .join(RegulatorGene,RegulatoryInteraction.regulator_gene_id == RegulatorGene.id)
            .join(TargetGene, RegulatoryInteraction.target_gene_id == TargetGene.id)
            .filter(RegulatoryInteraction.regulatory_cluster==tf)
            .group_by(
                RegulatoryInteraction.regulatory_cluster,
                RegulatoryInteraction.target_cluster,
                RegulatoryInteraction.direction
            )
        )
    else: 
        query =(
            database.session.query(
                RegulatoryInteraction.regulatory_cluster,
                RegulatoryInteraction.target_cluster,
                RegulatoryInteraction.direction
            ).filter(RegulatoryInteraction.regulatory_cluster==tf)
            .distinct() 
        )
    return query.all()

def get_gene_groups(genes):
    
    if not genes:
        return {}
  
    RegulatorGene = aliased(Gene)
    TargetGene = aliased(Gene)

    target_results =(
            database.session.query(
                TargetGene.gene_name,
                RegulatoryInteraction.target_cluster
                )
                .join(TargetGene, RegulatoryInteraction.target_gene_id == TargetGene.id)
                .filter(
                    TargetGene.gene_name.in_(genes)
                ).distinct()
                ).all()

    regulator_results =  ( 
                database.session.query(
                RegulatorGene.gene_name,
                RegulatoryInteraction.regulatory_cluster,
                )
                .join(RegulatorGene, RegulatoryInteraction.regulator_gene_id == RegulatorGene.id)
                .filter(
                    RegulatorGene.gene_name.in_(genes) 
                ).distinct()
            ).all()

    results = {gene: {'target_clusters':[],"regulatory_clusters":[]} for gene in genes}
    for gene_name, target_cluster in target_results:
        results[gene_name]["target_clusters"].append((target_cluster,))
    
    for gene_name, reg_cluster in regulator_results:
        results[gene_name]["regulatory_clusters"].append((reg_cluster,))
    
    return results

@st.cache_data
def get_tf_groups():
    result = sorted([r[0] for r in database.session.query(RegulatoryInteraction.regulatory_cluster).distinct()])
    return result

@st.cache_data
def get_genes_list():
    result = [r[0] for r in database.session.query(Gene.gene_name).filter(Gene.species_id==1)] 
    return result

def switch_tab(tab):
    st.session_state.grn = tab

def on_tab_change():
    st.toast(f"You opened the {st.session_state.grn} tab.")

st.title("Gene Regulatory Network")
st.divider()
database = db.DB()


st.image("server/images/Fig5_grn.tiff",width=600)
st.caption("Figure 5. Reconstruction of gene regulatory network using a consensus approach. (Reference paper?)")


clusters, gene_info = st.tabs(
    ['TF group info', 'Gene info']
)
if clusters.open:
    with clusters:
        st.markdown("""
            - Enter ID of a TF group from the above figure and the Data Explorer will list all the TG clusters predicted to be regulated. 
            """)


        TFs = get_tf_groups()
        verbose = st.checkbox("Show all genes in clusters (aggregated into lists for readability)")
        selected_tf = st.selectbox("Enter factor",TFs, index=None,label_visibility="hidden", placeholder="Select a transcription factor...")
        clusters = get_clusters(selected_tf, verbose)
        if selected_tf is not None:
            st.dataframe(clusters)
            st.caption("💡 Tip: Data can be downloaded as CSV using button in top-right corner of the table")


if gene_info.open:
    with gene_info:
        st.markdown("""
                    - Enter _X. elegans_ ID and retrieve all the TF and Target gene groups 
                    """)
        
        # Grab gene names from DB and show list to user, but only allows for selecting one at a time
        # x_elegans_genes = get_genes_list()
        # selected_gene = st.selectbox("Enter gene ID",x_elegans_genes, index=None,label_visibility="hidden", placeholder="Select an X elegans gene ID...")
        selected_genes = parse_input(st.text_area("Enter X. elegans gene IDs separated by space, comma or new line"))

        gene_groups = get_gene_groups(selected_genes)
        if selected_genes:
            gene_groups = get_gene_groups(selected_genes)
            
            # Transform results into a single DataFrame
            display_data = []
            for gene in gene_groups:
                display_data.append({
                    "Gene ID": gene,
                    "Regulatory Clusters": ", ".join([cluster[0] for cluster in gene_groups[gene]['regulatory_clusters']]) if gene_groups[gene]['regulatory_clusters'] else "None",
                    "Target Clusters": ", ".join([cluster[0] for cluster in gene_groups[gene]['target_clusters']]) if gene_groups[gene]['target_clusters'] else "None"
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.caption("💡 Tip: Data can be downloaded as CSV using button in top-right corner of the table")

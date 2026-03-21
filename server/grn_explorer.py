import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
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

def get_gene_groups(gene):
    RegulatorGene = aliased(Gene)
    TargetGene = aliased(Gene)
    
    target_clusters = (
            database.session.query(
            RegulatoryInteraction.target_cluster
            )
            .join(TargetGene, RegulatoryInteraction.target_gene_id == TargetGene.id)
            .filter(
                 TargetGene.gene_name == gene
            ).distinct()
            ).all()
    regulatory_clusters =  ( 
            database.session.query(
            RegulatoryInteraction.regulatory_cluster,
            )
            .join(RegulatorGene, RegulatoryInteraction.regulator_gene_id == RegulatorGene.id)
            .filter(
                RegulatorGene.gene_name == gene 
            ).distinct()
        ).all()
    
    results = {"target_clusters":target_clusters, "regulatory_clusters":regulatory_clusters}

    return results


@st.cache_data
def get_tf_groups():
    result = [r[0] for r in database.session.query(RegulatoryInteraction.regulatory_cluster).distinct()]
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

if gene_info.open:
    with gene_info:
        st.markdown("""
                    - Enter _X. elegans_ ID and retrieve all the TF and Target gene groups 
                    """)
        x_elegans_genes = get_genes_list()
        selected_gene = st.selectbox("Enter gene ID",x_elegans_genes, index=None,label_visibility="hidden", placeholder="Select an X elegans gene ID...")
        gene_groups = get_gene_groups(selected_gene)
        if selected_gene is not None:
            gene_groups = get_gene_groups(selected_gene)
            
            # Display regulatory clusters (where gene is a regulator)
            st.subheader("Regulatory Clusters")
            if gene_groups['regulatory_clusters']:
                st.dataframe(gene_groups['regulatory_clusters'])
            else:
                st.info(f"No regulatory clusters found where {selected_gene} acts as a regulator.")
            
            # Display target clusters (where gene is a target)
            st.subheader("Target Clusters")
            if gene_groups['target_clusters']:
                st.dataframe(gene_groups['target_clusters'])
            else:
                st.info(f"No target clusters found where {selected_gene} is a target.")
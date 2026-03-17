import streamlit as st
import pandas as pd
from datetime import datetime 
import database.db as db  # Your custom db module
from utils.constants import GENE_SELECTION_OPTIONS
from utils.helper_functions import parse_input, retreive_query_data
from database.models import RegulatoryInteraction, Gene, Species



st.title("Gene Regulatory Network")
st.divider()
database = db.DB()


st.image("server/images/Fig5_grn.tiff",width=600)
st.caption("Figure 5. Reconstruction of gene regulatory network using a consensus approach. (Reference paper?)")
st.markdown("""
            - Enter ID of a TF group from the above figure (eg C2H2:2)- and the Data Explorer will list" \
" all the _X. elegans_ IDs in this group, as well as all the TG clusters predicted to be regulated. 
            - This returns the list of gene IDs to explore the promoter regions of the listed genes to identify those that have cognate response elements, and which might represent true targets.""")


# TODO retreive these TFs from the database instead of hardcoding
TFs = [
    "C2H2:2",
    "ERF/DREB:2",
    "MYB:2",
    "HSF:1",
    "HD-ZIP:1",
    "AP2:2",
    "GATA:2",
    "MIKC:1",
    "NAC:1",
    "TCP:2",
    "GARP-G2-like:1",
    "GATA:1",
    "RWP-RK:1",
    "LAV:1",
    "C3H:1",
    "ERF/DREB:1",
    "FRS-FRF:2",
    "bZIP:1",
    "bHLH:2",
    "Trihelix:2",
    "NAC:2",
    "WRKY:1",
    "Trihelix:1",
    "E2F:2",
    "LAV:2",
    "MYB:1",
    "LBD:2",
    "M alpha:2",
    "MYB-related:1",
    "bHLH:1",
    "TCP:1",
    "LBD:1",
    "BES/BZR:1",
    "GARP-ARR-B:2",
]

selected_tf = st.selectbox("",TFs, index=None, placeholder="Select a transcription factor...")
st.write(f"Selected: {selected_tf}")


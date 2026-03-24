import streamlit as st
from pathlib import Path

# Get absolute paths for images to ensure they load on first app startup
SCRIPT_DIR = Path(__file__).parent
IMAGE_DIR = SCRIPT_DIR / "images"

st.markdown(
        """
       
            # Welcome to _Xerophyta_ Data Explorer!
            This tool simplifies the exploration of our transcriptomic datasets. Quickly find information pertaining to _Xerophyta_ genes using their gene names, _Arabidopsis_ IDs, GO terms, or protein domains.
        """,
        unsafe_allow_html=True
    )

# col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center", border=True)

# col1.write("X. elegans")
# col1.image("server/images/x_elegans_plant.png")

# col2.write("X. schlechteri")
# col2.image("server/images/x_schlechteri_plant.png")

# col3.subheader("**X. humilis**")
# col3.image("server/images/x_humilis_plant.png")

st.markdown("### Information")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["_**X. elegans**_", "**Gene expression page**","**Gene Info page**","**Gene Regulatory Network page**", "**About the lab**"])

with tab1:
    st.subheader("_X. elegans_")
    
    col1, col2 = st.columns([0.25,0.7], gap="small")

    col1.image(str(IMAGE_DIR / "x_elegans_plant.png"), width=250)
    col2.markdown("""
The genus _Xerophyta_, found in the subtropical regions of sub-Saharan Africa, Madagascar, and the Arabian Peninsula, contains 45 species, all of which exhibit vegetative desiccation tolerance. _Xerophyta elegans_ (formerly _Talbotia elegans_) is the only homoiochlorophyllous _Xerophyta_ species, all other _Xerophyta_ species are poikilochlorophyllous, degrading chlorophyll and dismantling plastids during desiccation. The dry leaves of _X. elegans_, which retain their chlorophyll are protected from photodamage by purple anthocyanins, and by their growth in deep shade along forested riverbanks or in the shadow of cave or cliff overhangs, in the foothills of the Drakensberg in South Africa.

This _X. elegans_ seedlings time-course transcriptome dataset comprises samples taken from seven time points while two leaf stage seedlings dehydrate, in an controlled environment,  from full hydration to less than 5% relative water content over 72 hours, and seven time points when the rehydrate over 48 hours.

**Reference:**
Kabwe E.N.K, Edwards M.P., Lyall R., Ngcala M., Schlebusch S.A., Marketos, O.P., VanBuren R., , Zoran Nikoloski Z., Ingle R.A. and Illing N. Transcriptional regulation of the response to water availability in the resurrection plant Xerophyta elegans. Submitted manuscript.
""")

with tab2:
    st.markdown("""
                - Visualise time-series gene expression profiles during dehydration and rehydration treatments. 
                - Filter results by differential expression status (up-regulated, down-regulated, or all genes) and customise plot display options. 
                - Download the expression plots and underlying data.""")
    st.page_link("server/expression_page.py", label="Click here for Gene expression page", icon="📊")

with tab3:

    st.markdown("""
                - Query the database to retrieve gene annotation information including BLAST annotations, Gene Ontology terms, enzyme codes, and InterPro domains.
                -  Search by Xerophyta gene ID, Arabidopsis ortholog, GO term, or enzyme code. 
                - Results can be downloaded as CSV or FASTA files.""")
    st.page_link("server/gene_query_page.py", label="Click here for Gene info page", icon="📑")
with tab4:
    st.markdown("""
                - Explore inferred transcriptional regulatory interactions between transcription factors and their target genes. 
                - Query info on a genes regulatory clusters and direction of regulation 
                """)
    st.page_link("server/grn_explorer.py", label="Click here for Gene Regulatory Network page", icon="🌐")


with tab5:
    st.image(str(IMAGE_DIR / "EvoDevo_lab.jpg"))


st.divider()

st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")


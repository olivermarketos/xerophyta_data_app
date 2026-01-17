import streamlit as st

st.markdown(
        """
       
            # Welcome to Xerophyta Data Explorer!</h3>
            This tool simplifies the exploration of our transcriptomic datasets. Quickly find Xerophyta genes using Arabidopsis symbols/IDs, GO terms, or protein domains, allowing you to focus on your genes of interest.
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

st.subheader("Xerophyta species information")
with st.expander("_click to expand_", expanded=True, icon= "🌱"):
    tab1, tab2, tab3, tab4 = st.tabs(["X. elegans", "X. schlechteri", "X. humilis", "About the lab"])

    with tab1:
        st.subheader("X. elegans")
        # st.link_button("X. elegans", 
        #                type="tertiary", 
        #                url="https://en.wikipedia.org/wiki/Xerophyta_elegans",
        #                icon="🔗")
        col1, col2 = st.columns([0.25,0.7], gap="small")

        col1.image("server/images/x_elegans_plant.png", width=250 )
        col2.write("Some description about species and experiments, links etc...")

    with tab2:
        st.subheader("X. schlechteri")

        col1, col2 = st.columns([0.25,0.7], gap="small")

        col1.image("server/images/x_schlechteri_plant.png", width=250 )
        col2.write("Some description about species and experiments, links etc...")
        

    with tab3:
        st.subheader("**X. humilis**")

        col1, col2 = st.columns([0.25,0.7], gap="small")

        col1.image("server/images/x_humilis_plant.png", width=250 )
        col2.write("Some description about species and experiments, links etc...")

    with tab4:
        st.subheader("EvoDevo lab")
st.subheader("Interface description")

with st.expander("_click to expand_", expanded=True, icon="ℹ️"):
    st.markdown("#### Gene info page")
    st.page_link("server/gene_query_page.py", label="Click here for Gene info page", icon="📑")
    st.write("Query the database to retrieve gene annotation information including BLAST annotations, Gene Ontology terms, enzyme codes, and InterPro domains. Search by Xerophyta gene ID, Arabidopsis ortholog, GO term, or enzyme code. Results can be downloaded as CSV or FASTA files.")

    st.divider()

    st.markdown("#### Gene expression page")
    st.page_link("server/expression_page.py", label="Click here for Gene expression page", icon="📊")
    st.write("Visualise time-series gene expression profiles during dehydration and rehydration treatments. Filter results by differential expression status (up-regulated, down-regulated, or all genes) and customise plot display options. Expression plots and underlying data can be downloaded.")

    st.divider()

    st.markdown("#### Gene Regulatory Network page")
    st.page_link("server/grn_explorer.py", label="Click here for Gene Regulatory Network page", icon="🌐")
    st.write("Explore inferred transcriptional regulatory interactions between transcription factors and their target genes. Filter by regulator gene, target gene, regulatory cluster, or direction of regulation (activation/repression). Currently available for X. elegans only.")


st.divider()

st.caption("To report a bug or suggest a feature, please contact olivermarketos@gmail.com.")


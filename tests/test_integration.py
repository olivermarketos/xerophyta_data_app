import pytest
from unittest.mock import patch, Mock
import pandas as pd
from database.db import DB
from database.models import Species, Gene, Annotation, GO, ArabidopsisHomologue
from utils.helper_functions import parse_input, retreive_query_data


class TestIntegration:
    """Integration tests for core workflows."""
    
    def test_complete_gene_query_workflow(self, db_instance):
        """Test complete workflow from gene input to data retrieval."""
        # Setup test data
        species = db_instance.add_species("X. elegans")
        gene = db_instance.add_genes_from_fasta(
            species.id, 
            "Xele.ptg000001l.104", 
            "ATGCGATCG"
        )
        
        # Add annotation
        annotation = Annotation(
            gene_id=gene.id,
            description="Test gene function",
            e_value=1e-10
        )
        db_instance.session.add(annotation)
        
        # Add GO term
        go_term = GO(
            go_id="GO:0003677",
            go_branch="F",
            go_name="DNA binding"
        )
        db_instance.session.add(go_term)
        db_instance.session.flush()
        
        # Link annotation to GO term
        annotation.go_ids.append(go_term)
        db_instance.session.commit()
        
        # Test the complete workflow
        input_text = "Xele.ptg000001l.104,nonexistent_gene"
        parsed_genes = parse_input(input_text)
        
        annotation_data, matched_input, missing_input = retreive_query_data(
            parsed_genes, "X. elegans", "Gene_ID"
        )
        
        # Assertions
        assert len(parsed_genes) == 2
        assert "Xele.ptg000001l.104" in parsed_genes
        assert "nonexistent_gene" in parsed_genes
        
        assert len(annotation_data) == 1
        assert annotation_data[0].gene_name == "Xele.ptg000001l.104"
        assert len(annotation_data[0].annotations) == 1
        assert len(annotation_data[0].annotations[0].go_ids) == 1
        
        assert "xele.ptg000001l.104" in matched_input
        assert "nonexistent_gene" in missing_input

    def test_arabidopsis_homologue_workflow(self, db_instance):
        """Test workflow for Arabidopsis homologue queries."""
        # Setup test data
        species = db_instance.add_species("X. elegans")
        gene = db_instance.add_genes_from_fasta(
            species.id, 
            "Xele.ptg000001l.104", 
            "ATGCGATCG"
        )
        
        # Add Arabidopsis homologue
        homologue = ArabidopsisHomologue(
            a_thaliana_locus="AT1G01010",
            a_thaliana_common_name="NAC domain protein"
        )
        db_instance.session.add(homologue)
        db_instance.session.flush()
        
        # Link gene to homologue
        gene.arabidopsis_homologues.append(homologue)
        db_instance.session.commit()
        
        # Test workflow by Arabidopsis locus
        input_loci = ["AT1G01010", "AT1G01020"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_loci, "X. elegans", "Arab_loci"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert annotation_data[0].gene_name == "Xele.ptg000001l.104"
        assert len(annotation_data[0].arabidopsis_homologues) == 1
        assert annotation_data[0].arabidopsis_homologues[0].a_thaliana_locus == "AT1G01010"
        
        assert "at1g01010" in matched_input
        assert "at1g01020" in missing_input

    def test_go_term_search_workflow(self, db_instance):
        """Test workflow for GO term searches."""
        # Setup test data
        species = db_instance.add_species("X. elegans")
        gene = db_instance.add_genes_from_fasta(
            species.id, 
            "Xele.ptg000001l.104", 
            "ATGCGATCG"
        )
        
        annotation = Annotation(gene_id=gene.id)
        db_instance.session.add(annotation)
        
        go_term = GO(
            go_id="GO:0003677",
            go_branch="F",
            go_name="DNA binding"
        )
        db_instance.session.add(go_term)
        db_instance.session.flush()
        
        annotation.go_ids.append(go_term)
        db_instance.session.commit()
        
        # Test GO ID search
        input_go_ids = ["GO:0003677", "GO:0006355"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_go_ids, "X. elegans", "GO_id"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert "0003677" in matched_input
        assert "0006355" in missing_input
        
        # Test GO name search
        input_go_names = ["DNA", "RNA"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_go_names, "X. elegans", "GO_name"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert "DNA" in matched_input
        assert "RNA" in missing_input

    @patch('database.db.pd.read_sql')
    def test_expression_data_workflow(self, mock_read_sql, db_instance):
        """Test expression data retrieval workflow."""
        # Mock expression data
        mock_expression_df = pd.DataFrame({
            'gene_name': ['Xele.ptg000001l.104', 'Xele.ptg000002l.205'],
            'treatment': ['Control', 'Stress'],
            'time': [0, 24],
            'normalised_expression': [1.5, 2.3],
            'log2_expression': [0.58, 1.20],
            'species_name': ['X. elegans', 'X. elegans']
        })
        mock_read_sql.return_value = mock_expression_df
        
        # Test expression data retrieval
        gene_list = ['Xele.ptg000001l.104', 'Xele.ptg000002l.205']
        expression_data = db_instance.get_expression_data(gene_list, 'X. elegans')
        
        # Assertions
        assert not expression_data.empty
        assert len(expression_data) == 2
        assert 'gene_name' in expression_data.columns
        assert 'normalised_expression' in expression_data.columns
        assert 'log2_expression' in expression_data.columns

    def test_multi_species_workflow(self, db_instance):
        """Test workflow with multiple species."""
        # Setup test data for multiple species
        species1 = db_instance.add_species("X. elegans")
        species2 = db_instance.add_species("X. humilis")
        
        gene1 = db_instance.add_genes_from_fasta(
            species1.id, 
            "Xele.ptg000001l.104", 
            "ATGCGATCG"
        )
        gene2 = db_instance.add_genes_from_fasta(
            species2.id, 
            "Xhum.ptg000001l.104", 
            "ATGCGATCG"
        )
        
        # Test species-specific queries
        elegans_genes = db_instance.get_genes_in_species("X. elegans")
        humilis_genes = db_instance.get_genes_in_species("X. humilis")
        
        # Assertions
        elegans_gene_names = [g.gene_name for g in elegans_genes]
        humilis_gene_names = [g.gene_name for g in humilis_genes]
        
        assert "Xele.ptg000001l.104" in elegans_gene_names
        assert "Xele.ptg000001l.104" not in humilis_gene_names
        assert "Xhum.ptg000001l.104" in humilis_gene_names
        assert "Xhum.ptg000001l.104" not in elegans_gene_names

    def test_error_handling_workflow(self, db_instance):
        """Test error handling in workflows."""
        # Test with empty input
        empty_result = parse_input("")
        assert empty_result == []
        
        # Test with invalid species
        annotation_data, matched_input, missing_input = retreive_query_data(
            ["test_gene"], "Invalid Species", "Gene_ID"
        )
        
        assert len(annotation_data) == 0
        assert len(matched_input) == 0
        assert "test_gene" in missing_input

    def test_large_input_workflow(self, db_instance):
        """Test workflow with large number of inputs."""
        # Setup test data
        species = db_instance.add_species("X. elegans")
        
        # Create multiple genes
        gene_names = [f"test_gene_{i}" for i in range(100)]
        for gene_name in gene_names[:50]:  # Only add first 50 to database
            db_instance.add_genes_from_fasta(species.id, gene_name, "ATGC")
        
        # Test with all 100 gene names
        annotation_data, matched_input, missing_input = retreive_query_data(
            gene_names, "X. elegans", "Gene_ID"
        )
        
        # Assertions
        assert len(annotation_data) == 50  # Only 50 were added to database
        assert len(matched_input) == 50
        assert len(missing_input) == 50

    def test_complex_annotation_workflow(self, db_instance):
        """Test workflow with complex annotation data."""
        # Setup comprehensive test data
        species = db_instance.add_species("X. elegans")
        gene = db_instance.add_genes_from_fasta(
            species.id, 
            "Xele.ptg000001l.104", 
            "ATGCGATCG"
        )
        
        # Create annotation with multiple GO terms and enzyme codes
        annotation = Annotation(
            gene_id=gene.id,
            description="Multi-functional enzyme",
            e_value=1e-15,
            similarity=98.5
        )
        db_instance.session.add(annotation)
        
        # Add multiple GO terms
        go_terms = [
            GO(go_id="GO:0003677", go_branch="F", go_name="DNA binding"),
            GO(go_id="GO:0006355", go_branch="P", go_name="regulation of transcription")
        ]
        for go_term in go_terms:
            db_instance.session.add(go_term)
        
        db_instance.session.flush()
        
        # Link annotation to GO terms
        for go_term in go_terms:
            annotation.go_ids.append(go_term)
        
        db_instance.session.commit()
        
        # Test retrieval by different GO search methods
        go_id_result, _, _ = retreive_query_data(
            ["GO:0003677"], "X. elegans", "GO_id"
        )
        go_name_result, _, _ = retreive_query_data(
            ["DNA"], "X. elegans", "GO_name"
        )
        
        # Assertions
        assert len(go_id_result) == 1
        assert len(go_name_result) == 1
        assert go_id_result[0].gene_name == "Xele.ptg000001l.104"
        assert go_name_result[0].gene_name == "Xele.ptg000001l.104"
        assert len(go_id_result[0].annotations[0].go_ids) == 2
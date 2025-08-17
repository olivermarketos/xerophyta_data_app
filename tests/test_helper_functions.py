import pytest
from unittest.mock import Mock, patch
from utils.helper_functions import parse_input, retreive_query_data


class TestHelperFunctions:
    """Test utility helper functions."""
    
    def test_parse_input_empty(self):
        """Test parsing empty input."""
        result = parse_input("")
        assert result == []
        
        result = parse_input("   ")
        assert result == []

    def test_parse_input_single_item(self):
        """Test parsing single item."""
        result = parse_input("gene1")
        assert result == ["gene1"]
        
        result = parse_input("  gene1  ")
        assert result == ["gene1"]

    def test_parse_input_comma_separated(self):
        """Test parsing comma-separated items."""
        result = parse_input("gene1,gene2,gene3")
        assert set(result) == {"gene1", "gene2", "gene3"}
        
        result = parse_input("gene1, gene2 , gene3")
        assert set(result) == {"gene1", "gene2", "gene3"}

    def test_parse_input_newline_separated(self):
        """Test parsing newline-separated items."""
        result = parse_input("gene1\ngene2\ngene3")
        assert set(result) == {"gene1", "gene2", "gene3"}

    def test_parse_input_mixed_separators(self):
        """Test parsing with mixed separators."""
        result = parse_input("gene1,gene2\ngene3")
        assert set(result) == {"gene1", "gene2", "gene3"}

    def test_parse_input_duplicates(self):
        """Test that duplicates are removed."""
        result = parse_input("gene1,gene1,gene2")
        assert set(result) == {"gene1", "gene2"}
        assert len(result) == 2

    def test_parse_input_empty_items(self):
        """Test that empty items are filtered out."""
        result = parse_input("gene1,,gene2,")
        assert set(result) == {"gene1", "gene2"}

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_gene_id(self, mock_db_class):
        """Test query data retrieval by Gene ID."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        # Mock gene objects
        mock_gene1 = Mock()
        mock_gene1.gene_name = "Gene1"
        mock_gene2 = Mock()
        mock_gene2.gene_name = "Gene2"
        
        mock_db.get_gene_annotation_data.return_value = [mock_gene1, mock_gene2]
        
        # Test
        input_genes = ["gene1", "gene2", "gene3"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "Gene_ID"
        )
        
        # Assertions
        assert len(annotation_data) == 2
        assert "gene1" in matched_input or "gene2" in matched_input
        mock_db.get_gene_annotation_data.assert_called_once_with(
            input_genes, "xerophyta_gene_name", "X. elegans"
        )

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_arab_loci(self, mock_db_class):
        """Test query data retrieval by Arabidopsis loci."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        # Mock gene with arabidopsis homologue
        mock_homologue = Mock()
        mock_homologue.a_thaliana_locus = "AT1G01010"
        
        mock_gene = Mock()
        mock_gene.arabidopsis_homologues = [mock_homologue]
        
        mock_db.get_gene_annotation_data.return_value = [mock_gene]
        
        # Test
        input_genes = ["AT1G01010", "AT1G01020"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "Arab_loci"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert "at1g01010" in matched_input
        assert "at1g01020" in missing_input

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_go_id(self, mock_db_class):
        """Test query data retrieval by GO ID."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.normalize_go_term.side_effect = lambda x: x.replace("GO:", "")
        
        # Mock gene with GO annotation
        mock_go = Mock()
        mock_go.go_id = "GO:0003677"
        
        mock_annotation = Mock()
        mock_annotation.go_ids = [mock_go]
        
        mock_gene = Mock()
        mock_gene.annotations = [mock_annotation]
        
        mock_db.get_gene_annotation_data.return_value = [mock_gene]
        
        # Test
        input_genes = ["GO:0003677", "GO:0006355"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "GO_id"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        mock_db.normalize_go_term.assert_called()

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_no_results(self, mock_db_class):
        """Test query data retrieval with no results."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.get_gene_annotation_data.return_value = []
        
        # Test
        input_genes = ["nonexistent_gene"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "Gene_ID"
        )
        
        # Assertions
        assert len(annotation_data) == 0
        assert len(matched_input) == 0
        assert "nonexistent_gene" in missing_input

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_go_name(self, mock_db_class):
        """Test query data retrieval by GO name."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        # Mock gene with GO annotation
        mock_go = Mock()
        mock_go.go_name = "DNA binding"
        
        mock_annotation = Mock()
        mock_annotation.go_ids = [mock_go]
        
        mock_gene = Mock()
        mock_gene.annotations = [mock_annotation]
        
        mock_db.get_gene_annotation_data.return_value = [mock_gene]
        
        # Test
        input_genes = ["dna", "rna"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "GO_name"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert "dna" in matched_input
        assert "rna" in missing_input

    @patch('utils.helper_functions.db.DB')
    def test_retreive_query_data_enzyme_code(self, mock_db_class):
        """Test query data retrieval by enzyme code."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        # Mock gene with enzyme annotation
        mock_enzyme = Mock()
        mock_enzyme.enzyme_code = "EC:1.1.1.1"
        
        mock_annotation = Mock()
        mock_annotation.enzyme_codes = [mock_enzyme]
        
        mock_gene = Mock()
        mock_gene.annotations = [mock_annotation]
        
        mock_db.get_gene_annotation_data.return_value = [mock_gene]
        
        # Test
        input_genes = ["1.1.1.1", "2.2.2.2"]
        annotation_data, matched_input, missing_input = retreive_query_data(
            input_genes, "X. elegans", "EC_code"
        )
        
        # Assertions
        assert len(annotation_data) == 1
        assert "EC:1.1.1.1" in matched_input
        assert "2.2.2.2" in missing_input
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from database.db import DB
from database.models import Species, Gene, Annotation, GO, ArabidopsisHomologue


class TestDB:
    """Test database operations."""
    
    def test_add_species(self, db_instance):
        """Test adding a new species."""
        species = db_instance.add_species("X. elegans")
        
        assert species is not None
        assert species.name == "X. elegans"
        
        # Test adding the same species again (should return existing)
        species2 = db_instance.add_species("X. elegans")
        assert species.id == species2.id

    def test_add_genes_from_fasta(self, db_instance, sample_gene_data):
        """Test adding genes from FASTA data."""
        # First add a species
        species = db_instance.add_species(sample_gene_data['species_name'])
        
        # Add a gene
        gene = db_instance.add_genes_from_fasta(
            species.id, 
            sample_gene_data['gene_names'][0], 
            "ATGCGATCGATCG"
        )
        
        assert gene is not None
        assert gene.gene_name == sample_gene_data['gene_names'][0]
        assert gene.species_id == species.id
        assert gene.coding_sequence == "ATGCGATCGATCG"
        
        # Test adding the same gene again (should return existing)
        gene2 = db_instance.add_genes_from_fasta(
            species.id, 
            sample_gene_data['gene_names'][0], 
            "DIFFERENT_SEQUENCE"
        )
        assert gene.id == gene2.id

    def test_normalize_go_term(self, db_instance):
        """Test GO term normalization."""
        # Test with standard GO term
        result = db_instance.normalize_go_term("GO:0003677")
        assert result == "0003677"
        
        # Test with already normalized term
        result = db_instance.normalize_go_term("0003677")
        assert result == "0003677"
        
        # Test with lowercase
        result = db_instance.normalize_go_term("go:0003677")
        assert result == "0003677"

    def test_get_all_species(self, db_instance):
        """Test retrieving all species."""
        # Add test species
        db_instance.add_species("X. elegans")
        db_instance.add_species("X. humilis")
        
        species = db_instance.get_all_species()
        
        assert len(species) >= 2
        species_names = [s.name for s in species]
        assert "X. elegans" in species_names
        assert "X. humilis" in species_names

    @patch('database.db.pd.read_sql')
    def test_get_expression_data(self, mock_read_sql, db_instance):
        """Test getting expression data."""
        # Mock the pandas read_sql response
        mock_df = pd.DataFrame({
            'gene_name': ['gene1', 'gene2'],
            'normalised_expression': [1.5, 2.3],
            'log2_expression': [0.58, 1.20]
        })
        mock_read_sql.return_value = mock_df
        
        result = db_instance.get_expression_data(['gene1', 'gene2'], 'X. elegans')
        
        assert not result.empty
        assert len(result) == 2
        mock_read_sql.assert_called_once()

    def test_get_genes_in_species(self, db_instance, sample_gene_data):
        """Test getting genes for a specific species."""
        # Add test data
        species = db_instance.add_species(sample_gene_data['species_name'])
        for gene_name in sample_gene_data['gene_names']:
            db_instance.add_genes_from_fasta(species.id, gene_name, "ATGC")
        
        genes = db_instance.get_genes_in_species(sample_gene_data['species_name'])
        
        assert len(genes) >= len(sample_gene_data['gene_names'])
        gene_names = [g.gene_name for g in genes]
        for expected_gene in sample_gene_data['gene_names']:
            assert expected_gene in gene_names

    def test_database_connection(self, db_instance):
        """Test that database connection is working."""
        assert db_instance.engine is not None
        assert db_instance.session is not None
        assert db_instance.conn is not None

    def test_session_cleanup(self, db_instance):
        """Test that database sessions can be properly closed."""
        db_instance.session.close()
        db_instance.conn.close()
        # Should not raise an exception
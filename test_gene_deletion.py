#!/usr/bin/env python3
"""
Test script for gene deletion functionality.
This script demonstrates how to use the delete_genes_by_names method.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import DB
import database.models as models

def test_gene_deletion():
    """Test the gene deletion functionality with sample data"""
    
    # Initialize database connection
    db = DB()
    
    # First, let's see what genes we have available
    print("=== Available Genes Sample ===")
    sample_gene = db.session.query(models.Gene).first()
    if sample_gene:
        print(f"Sample gene found: {sample_gene.gene_name}")
    else:
        print("No genes found in database")
        return
    
    # Get a few gene names for testing
    all_genes = db.session.query(models.Gene).limit(5).all()
    if not all_genes:
        print("No genes found in database for testing")
        return
    
    test_gene_names = [str(gene.gene_name) for gene in all_genes[:2]]  # Ensure all are strings
    test_gene_names.append("Xele.ptg000003l.1201")

    print(f"Testing deletion with genes: {test_gene_names}")
    
    # Test 1: Dry run to see what would be deleted
    print("\n=== DRY RUN TEST ===")
    dry_run_result = db.delete_genes_by_names(test_gene_names, dry_run=True)
    print("Dry run result:")
    for key, value in dry_run_result.items():
        print(f"  {key}: {value}")
    
    # Test 2: Test with non-existent genes
    print("\n=== NON-EXISTENT GENES TEST ===")
    fake_genes = ["FAKE_GENE_001", "FAKE_GENE_002"]
    fake_result = db.delete_genes_by_names(fake_genes, dry_run=True)
    print("Non-existent genes result:")
    for key, value in fake_result.items():
        print(f"  {key}: {value}")
    
    # Test 3: Mixed existing and non-existent genes
    print("\n=== MIXED GENES TEST ===")
    mixed_genes = [test_gene_names[0], "FAKE_GENE_003"]
    mixed_result = db.delete_genes_by_names(mixed_genes, dry_run=True)
    print("Mixed genes result:")
    for key, value in mixed_result.items():
        print(f"  {key}: {value}")
    
    print("\n=== TESTING COMPLETE ===")
    print("To actually delete genes, call delete_genes_by_names() without dry_run=True")
    print("Example usage:")
    print("  # Delete single gene")
    print("  result = db.delete_genes_by_names(['GENE_NAME'])")
    print()
    print("  # Delete multiple genes with orphan cleanup")
    print("  result = db.delete_genes_by_names(['GENE1', 'GENE2'], cleanup_orphans=True)")
    print()
    print("  # Preview deletion (dry run)")
    print("  result = db.delete_genes_by_names(['GENE_NAME'], dry_run=True)")

def example_usage():
    """Example of how to use the gene deletion functionality"""
    
    # Initialize database
    db = DB()
    
    # Example 1: Delete a single gene (dry run)
    gene_to_delete = "EXAMPLE_GENE_001"
    result = db.delete_genes_by_names([gene_to_delete], dry_run=True)
    
    if result['success']:
        print(f"Would delete gene {gene_to_delete} and:")
        print(f"- {result['annotations_deleted']} annotations")
        print(f"- {result['gene_expressions_deleted']} gene expressions")
        print(f"- {result['differential_expressions_deleted']} differential expressions")
        print(f"- {result['regulatory_interactions_deleted']} regulatory interactions")
        print(f"- {result['arabidopsis_homologue_associations_removed']} homologue associations")
    
    # Example 2: Delete multiple genes with cleanup
    # genes_to_delete = ["GENE_001", "GENE_002", "GENE_003"]
    # Uncomment the following line to actually perform deletion:
    # result = db.delete_genes_by_names(genes_to_delete, cleanup_orphans=True)
    
    # Example 3: Error handling
    try:
        result = db.delete_genes_by_names(["NONEXISTENT_GENE"])
        if not result['success']:
            print(f"Deletion failed: {result['error_message']}")
        else:
            print("Deletion completed successfully")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("Gene Deletion Functionality Test")
    print("=" * 40)
    
    try:
        test_gene_deletion()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"Error during testing: {e}")
# Gene Deletion Functionality

This document describes how to use the gene deletion functionality implemented in the `DB` class.

## Method: `delete_genes_by_names()`

The `delete_genes_by_names()` method allows you to delete genes and all their associated data from the database.

### Parameters

- `gene_names` (list or str): List of gene names to delete, or a single gene name as string
- `cleanup_orphans` (bool, optional): Whether to clean up orphaned annotation records (GO, Enzyme, InterPro, ArabidopsisHomologue). Default: False
- `dry_run` (bool, optional): If True, shows what would be deleted without actually deleting. Default: False

### Returns

A dictionary with detailed deletion summary:
```python
{
    'genes_requested': int,           # Number of genes requested for deletion
    'genes_found': int,              # Number of genes found in database
    'genes_deleted': int,            # Number of genes actually deleted
    'genes_not_found': list,         # List of gene names not found
    'annotations_deleted': int,       # Number of annotations deleted
    'gene_expressions_deleted': int,  # Number of gene expressions deleted
    'differential_expressions_deleted': int,  # Number of differential expressions deleted
    'regulatory_interactions_deleted': int,   # Number of regulatory interactions deleted
    'arabidopsis_homologue_associations_removed': int,  # Many-to-many associations removed
    'orphaned_records_cleaned': int,  # Orphaned records cleaned (if cleanup_orphans=True)
    'success': bool,                 # Whether operation succeeded
    'error_message': str             # Error message if operation failed
}
```

## What Gets Deleted

When you delete a gene, the following associated data is automatically removed:

1. **Annotations** - All annotation records for the gene
2. **Gene Expressions** - All RNA-seq expression data for the gene  
3. **Differential Expression** - All differential expression data for the gene
4. **Regulatory Interactions** - All interactions where the gene is either regulator or target
5. **Arabidopsis Homologue Associations** - Many-to-many relationships with A. thaliana genes

### Optional Cleanup

If `cleanup_orphans=True`, the method will also remove:
- GO terms with no remaining annotation associations
- Enzyme codes with no remaining annotation associations  
- InterPro records with no remaining annotation associations
- Arabidopsis homologue records with no remaining gene associations

## Usage Examples

### Basic Usage

```python
from database.db import DB

# Initialize database connection
db = DB()

# Delete a single gene
result = db.delete_genes_by_names("Xele.ptg000001l.1")
print(f"Deleted {result['genes_deleted']} genes")

# Delete multiple genes
gene_list = ["Gene1", "Gene2", "Gene3"]
result = db.delete_genes_by_names(gene_list)
```

### Preview Before Deletion (Dry Run)

```python
# See what would be deleted without actually deleting
result = db.delete_genes_by_names(["Gene1", "Gene2"], dry_run=True)
print(f"Would delete {result['genes_found']} genes:")
print(f"- {result['annotations_deleted']} annotations")
print(f"- {result['gene_expressions_deleted']} gene expressions")
print(f"- {result['regulatory_interactions_deleted']} regulatory interactions")
```

### Delete with Cleanup

```python
# Delete genes and clean up orphaned annotation records
result = db.delete_genes_by_names(gene_list, cleanup_orphans=True)
print(f"Cleaned up {result['orphaned_records_cleaned']} orphaned records")
```

### Error Handling

```python
try:
    result = db.delete_genes_by_names(gene_list)
    if result['success']:
        print(f"Successfully deleted {result['genes_deleted']} genes")
        if result['genes_not_found']:
            print(f"Genes not found: {result['genes_not_found']}")
    else:
        print(f"Deletion failed: {result['error_message']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Safety Features

1. **Transaction Management**: All deletions happen in a database transaction that is rolled back on error
2. **Validation**: Checks if genes exist before attempting deletion
3. **Dry Run Mode**: Preview deletions before executing them
4. **Detailed Reporting**: Comprehensive summary of what was deleted
5. **Error Handling**: Graceful handling of missing genes and database errors

## Testing

You can test the functionality using the provided test script:

```bash
uv run python test_gene_deletion.py
```

This will run several test scenarios including dry runs, non-existent genes, and mixed gene lists.
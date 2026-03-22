# SQLAlchemy ORM Cheatsheet

Quick reference for SQLAlchemy queries using your database models.

## Setup

```python
from database.models import Gene, RegulatoryInteraction, Annotation, Species, GO, EnzymeCode
from database.models import Gene_expressions, Experiments, DifferentialExpression
from sqlalchemy import func, or_, and_, distinct
import database.db as db

database = db.DB()
session = database.session
```

---

## Basic Queries

### Get all records
```python
# Get all genes
all_genes = session.query(Gene).all()

# Get all species
all_species = session.query(Species).all()
```

### Get first/one record
```python
# Get first gene
first_gene = session.query(Gene).first()

# Get specific gene by ID (returns None if not found)
gene = session.query(Gene).get(1)

# Get one (raises error if not found or multiple found)
gene = session.query(Gene).filter_by(gene_name="Xele.ptg000001l.104").one()

# Get one or none (safer)
gene = session.query(Gene).filter_by(gene_name="Xele.ptg000001l.104").one_or_none()
```

### Count records
```python
# Count all genes
count = session.query(Gene).count()

# Count with filter
count = session.query(Gene).filter(Gene.species_id == 1).count()
```

---

## Filtering

### Basic filtering - `filter_by()` (simple equality)
```python
# Single condition
genes = session.query(Gene).filter_by(species_id=1).all()

# Multiple conditions (AND)
genes = session.query(Gene).filter_by(
    species_id=1,
    gene_name="Xele.ptg000001l.104"
).all()
```

### Advanced filtering - `filter()` (comparisons, expressions)
```python
# Equality
genes = session.query(Gene).filter(Gene.species_id == 1).all()

# Not equal
genes = session.query(Gene).filter(Gene.species_id != 1).all()

# Greater than / Less than
interactions = session.query(RegulatoryInteraction).filter(
    RegulatoryInteraction.id > 100
).all()

# LIKE (case-sensitive pattern matching)
genes = session.query(Gene).filter(Gene.gene_name.like("%ptg%")).all()

# ILIKE (case-insensitive)
genes = session.query(Gene).filter(Gene.gene_name.ilike("%XELE%")).all()

# IN clause
gene_names = ["gene1", "gene2", "gene3"]
genes = session.query(Gene).filter(Gene.gene_name.in_(gene_names)).all()

# NOT IN
genes = session.query(Gene).filter(~Gene.gene_name.in_(gene_names)).all()

# IS NULL
genes = session.query(Gene).filter(Gene.coding_sequence.is_(None)).all()
# or
genes = session.query(Gene).filter(Gene.coding_sequence == None).all()

# IS NOT NULL
genes = session.query(Gene).filter(Gene.coding_sequence.isnot(None)).all()
# or
genes = session.query(Gene).filter(Gene.coding_sequence != None).all()

# BETWEEN
annotations = session.query(Annotation).filter(
    Annotation.e_value.between(0.0, 0.001)
).all()
```

### Combining conditions

```python
# AND - multiple filter() calls
genes = session.query(Gene)\
    .filter(Gene.species_id == 1)\
    .filter(Gene.gene_name.like("%ptg%"))\
    .all()

# AND - using and_()
from sqlalchemy import and_
genes = session.query(Gene).filter(
    and_(
        Gene.species_id == 1,
        Gene.gene_name.like("%ptg%")
    )
).all()

# OR
from sqlalchemy import or_
genes = session.query(Gene).filter(
    or_(
        Gene.species_id == 1,
        Gene.species_id == 2
    )
).all()

# Complex combinations
genes = session.query(Gene).filter(
    and_(
        Gene.species_id == 1,
        or_(
            Gene.gene_name.like("%ptg%"),
            Gene.gene_name.like("%scaffold%")
        )
    )
).all()
```

---

## Selecting Specific Columns

```python
# Select specific columns (returns tuples)
results = session.query(
    Gene.gene_name,
    Gene.species_id
).all()
# Result: [('gene1', 1), ('gene2', 1), ...]

# Select with labels
results = session.query(
    Gene.gene_name.label('name'),
    Gene.species_id.label('species')
).all()

# Select from multiple tables
results = session.query(
    Gene.gene_name,
    Species.name
).join(Species).all()
```

---

## Joins

### Implicit joins (using relationships)
```python
# Get gene with its species (relationship defined in model)
gene = session.query(Gene).filter_by(gene_name="some_gene").first()
species_name = gene.species.name  # Uses the relationship
```

### Explicit joins
```python
# Inner join (default)
results = session.query(Gene, Species)\
    .join(Species)\
    .all()

# Specify join condition explicitly
results = session.query(Gene)\
    .join(Species, Gene.species_id == Species.id)\
    .all()

# Left outer join
results = session.query(Gene)\
    .outerjoin(Species)\
    .all()

# Join with filter
results = session.query(Gene, Species)\
    .join(Species)\
    .filter(Species.name == "X. elegans")\
    .all()
```

### Joins with relationships
```python
# Join using relationship name (cleaner)
results = session.query(Gene)\
    .join(Gene.species)\
    .filter(Species.name == "X. elegans")\
    .all()

# Multiple joins
results = session.query(Gene)\
    .join(Gene.annotations)\
    .join(Annotation.go_ids)\
    .filter(GO.go_id == "GO:0005524")\
    .all()
```

### Aliased joins (for self-joins or multiple joins to same table)
```python
from sqlalchemy.orm import aliased

# For regulatory interactions (regulator and target are both Genes)
RegulatorGene = aliased(Gene, name="regulator")
TargetGene = aliased(Gene, name="target")

results = session.query(
    RegulatorGene.gene_name.label("regulator"),
    TargetGene.gene_name.label("target"),
    RegulatoryInteraction.direction
)\
    .join(RegulatorGene, RegulatoryInteraction.regulator_gene_id == RegulatorGene.id)\
    .join(TargetGene, RegulatoryInteraction.target_gene_id == TargetGene.id)\
    .all()
```

---

## Ordering, Limiting, and Pagination

### Order by
```python
# Ascending (default)
genes = session.query(Gene).order_by(Gene.gene_name).all()

# Descending
genes = session.query(Gene).order_by(Gene.gene_name.desc()).all()

# Multiple columns
genes = session.query(Gene)\
    .order_by(Gene.species_id, Gene.gene_name.desc())\
    .all()

# Order by related table column
genes = session.query(Gene)\
    .join(Species)\
    .order_by(Species.name)\
    .all()
```

### Limit and Offset
```python
# Limit (top N)
genes = session.query(Gene).limit(10).all()

# Offset (skip first N)
genes = session.query(Gene).offset(5).limit(10).all()

# Pagination
page = 2
per_page = 20
genes = session.query(Gene)\
    .offset((page - 1) * per_page)\
    .limit(per_page)\
    .all()
```

---

## Distinct

```python
# Distinct rows
species_ids = session.query(Gene.species_id).distinct().all()

# Distinct with multiple columns
clusters = session.query(
    RegulatoryInteraction.regulatory_cluster,
    RegulatoryInteraction.target_cluster
).distinct().all()

# Using func.distinct()
from sqlalchemy import distinct
species_ids = session.query(distinct(Gene.species_id)).all()
```

---

## Aggregations

### Count, Sum, Avg, Min, Max
```python
from sqlalchemy import func

# Count
gene_count = session.query(func.count(Gene.id)).scalar()

# Count distinct
species_count = session.query(func.count(distinct(Gene.species_id))).scalar()

# Average
avg_expression = session.query(
    func.avg(Gene_expressions.normalised_expression)
).scalar()

# Sum
total = session.query(func.sum(Annotation.bit_score)).scalar()

# Min / Max
min_val = session.query(func.min(Annotation.e_value)).scalar()
max_val = session.query(func.max(Annotation.e_value)).scalar()
```

### Group By
```python
# Group by with count
results = session.query(
    Gene.species_id,
    func.count(Gene.id).label('gene_count')
)\
    .group_by(Gene.species_id)\
    .all()

# Group by multiple columns
results = session.query(
    RegulatoryInteraction.regulatory_cluster,
    RegulatoryInteraction.target_cluster,
    func.count(RegulatoryInteraction.id).label('interaction_count')
)\
    .group_by(
        RegulatoryInteraction.regulatory_cluster,
        RegulatoryInteraction.target_cluster
    )\
    .all()

# Group by with having
results = session.query(
    Gene.species_id,
    func.count(Gene.id).label('count')
)\
    .group_by(Gene.species_id)\
    .having(func.count(Gene.id) > 100)\
    .all()
```

---

## Working with Relationships

### Eager Loading (prevent N+1 queries)

```python
from sqlalchemy.orm import joinedload, subqueryload

# joinedload - uses LEFT OUTER JOIN
genes = session.query(Gene)\
    .options(joinedload(Gene.species))\
    .all()
# Now gene.species doesn't trigger a new query

# subqueryload - uses separate SELECT
genes = session.query(Gene)\
    .options(subqueryload(Gene.annotations))\
    .all()
# Now gene.annotations doesn't trigger new queries

# Nested loading
genes = session.query(Gene)\
    .options(
        subqueryload(Gene.annotations)
        .subqueryload(Annotation.go_ids)
    )\
    .all()

# Multiple relationships
genes = session.query(Gene)\
    .options(
        joinedload(Gene.species),
        subqueryload(Gene.annotations),
        subqueryload(Gene.arabidopsis_homologues)
    )\
    .all()
```

### Accessing relationships
```python
# One-to-many
gene = session.query(Gene).first()
annotations = gene.annotations  # List of Annotation objects
species = gene.species  # Single Species object

# Many-to-many
annotation = session.query(Annotation).first()
go_terms = annotation.go_ids  # List of GO objects

# Back-references
species = session.query(Species).first()
genes = species.genes  # All genes for this species
```

---

## String Operations

```python
# Concatenation
from sqlalchemy import func
results = session.query(
    func.concat(Gene.gene_name, ' (', Species.name, ')')
).join(Species).all()

# Upper / Lower
results = session.query(func.upper(Gene.gene_name)).all()
results = session.query(func.lower(Gene.gene_name)).all()

# Length
results = session.query(Gene).filter(
    func.length(Gene.gene_name) > 20
).all()
```

---

## Subqueries

```python
# Subquery
from sqlalchemy import subquery

# Find genes that have annotations
subq = session.query(Annotation.gene_id).distinct().subquery()
genes_with_annotations = session.query(Gene).filter(
    Gene.id.in_(subq)
).all()

# Subquery with alias
subq = session.query(
    Gene_expressions.gene_id,
    func.avg(Gene_expressions.normalised_expression).label('avg_expr')
)\
    .group_by(Gene_expressions.gene_id)\
    .subquery()

results = session.query(Gene, subq.c.avg_expr)\
    .join(subq, Gene.id == subq.c.gene_id)\
    .all()
```

---

## Converting to Pandas DataFrame

```python
import pandas as pd

# Method 1: From query results
results = session.query(Gene).all()
df = pd.DataFrame([{
    'id': g.id,
    'gene_name': g.gene_name,
    'species_id': g.species_id
} for g in results])

# Method 2: Using pd.read_sql (recommended)
query = session.query(Gene).filter(Gene.species_id == 1)
df = pd.read_sql(query.statement, database.engine)

# Method 3: From specific columns
query = session.query(
    Gene.gene_name,
    Gene.species_id,
    Species.name.label('species_name')
).join(Species)
df = pd.read_sql(query.statement, database.engine)
```

---

## Creating, Updating, Deleting

### Create
```python
# Create single record
new_species = Species(name="X. villosa")
session.add(new_species)
session.commit()

# Create multiple records
genes = [
    Gene(gene_name="gene1", species_id=1),
    Gene(gene_name="gene2", species_id=1),
]
session.add_all(genes)
session.commit()

# Bulk insert (faster, but no ORM events)
session.bulk_insert_mappings(Gene, [
    {"gene_name": "gene1", "species_id": 1},
    {"gene_name": "gene2", "species_id": 1},
])
session.commit()
```

### Update
```python
# Update single record
gene = session.query(Gene).filter_by(gene_name="gene1").first()
gene.coding_sequence = "ATCG..."
session.commit()

# Update multiple records
session.query(Gene).filter(Gene.species_id == 1).update({
    Gene.coding_sequence: "UPDATED"
})
session.commit()
```

### Delete
```python
# Delete single record
gene = session.query(Gene).filter_by(gene_name="gene1").first()
session.delete(gene)
session.commit()

# Delete multiple records
session.query(Gene).filter(Gene.species_id == 1).delete()
session.commit()
```

---

## Common Patterns for Your Project

### Get all regulatory interactions for a cluster
```python
from sqlalchemy.orm import aliased

RegGene = aliased(Gene)
TarGene = aliased(Gene)

interactions = session.query(
    RegGene.gene_name.label('regulator'),
    TarGene.gene_name.label('target'),
    RegulatoryInteraction.direction
)\
    .join(RegGene, RegulatoryInteraction.regulator_gene_id == RegGene.id)\
    .join(TarGene, RegulatoryInteraction.target_gene_id == TarGene.id)\
    .filter(RegulatoryInteraction.regulatory_cluster == 'C2H2:2')\
    .all()

# Convert to DataFrame
df = pd.DataFrame(interactions, columns=['regulator', 'target', 'direction'])
```

### Get genes with specific GO term
```python
genes = session.query(Gene)\
    .join(Gene.annotations)\
    .join(Annotation.go_ids)\
    .filter(GO.go_id == 'GO:0005524')\
    .distinct()\
    .all()
```

### Get gene expression data with gene names
```python
results = session.query(
    Gene.gene_name,
    Gene_expressions.normalised_expression,
    Gene_expressions.treatment,
    Gene_expressions.time,
    Experiments.experiment_name
)\
    .join(Gene_expressions, Gene.id == Gene_expressions.gene_id)\
    .join(Experiments, Gene_expressions.experiment_id == Experiments.id)\
    .filter(Experiments.experiment_name == "drought_stress")\
    .all()

df = pd.DataFrame(results, columns=[
    'gene_name', 'expression', 'treatment', 'time', 'experiment'
])
```

### Get genes with annotations and species
```python
results = session.query(Gene)\
    .options(
        joinedload(Gene.species),
        subqueryload(Gene.annotations)
            .subqueryload(Annotation.go_ids),
        subqueryload(Gene.arabidopsis_homologues)
    )\
    .filter(Species.name == "X. elegans")\
    .all()
```

---

## Debugging

### Print SQL
```python
# Print the SQL for a query
query = session.query(Gene).filter(Gene.species_id == 1)
print(str(query.statement.compile(compile_kwargs={"literal_binds": True})))
```

### Enable SQL logging
```python
# In db.py, set echo=True
self.engine = sq.create_engine(f"sqlite:///{self.DATABASE_NAME}", echo=True)
```

---

## Common Gotchas

1. **Don't forget to commit**: Changes won't persist without `session.commit()`

2. **Session scope**: Be careful with long-lived sessions; they can hold stale data

3. **N+1 queries**: Use `joinedload` or `subqueryload` to avoid loading relationships in loops

4. **filter() vs filter_by()**:
   - `filter_by()`: keyword arguments, equality only
   - `filter()`: expressions, any comparison

5. **Lazy loading**: Accessing relationships after session close causes errors

6. **NULL checks**: Use `is_(None)` or `isnot(None)`, not `== None` (though `== None` works)

---

## Quick Reference Summary

| Task | Code |
|------|------|
| Get all | `session.query(Model).all()` |
| Get one | `session.query(Model).first()` |
| Filter | `session.query(Model).filter(Model.col == value)` |
| Filter simple | `session.query(Model).filter_by(col=value)` |
| Count | `session.query(Model).count()` |
| Join | `session.query(M1).join(M2)` |
| Order | `session.query(Model).order_by(Model.col)` |
| Limit | `session.query(Model).limit(10)` |
| Distinct | `session.query(Model.col).distinct()` |
| Group by | `query.group_by(Model.col)` |
| To DataFrame | `pd.read_sql(query.statement, engine)` |

---

## Resources

- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [SQLAlchemy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
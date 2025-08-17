import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import (
    Base, Species, Gene, Annotation, GO, EnzymeCode, InterPro, 
    ArabidopsisHomologue, Gene_expressions, Experiments, 
    DifferentialExpression, RegulatoryInteraction
)


class TestModels:
    """Test SQLAlchemy data models."""
    
    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Create database session for testing."""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_species_creation(self, session):
        """Test Species model creation."""
        species = Species(name="X. elegans")
        session.add(species)
        session.commit()
        
        assert species.id is not None
        assert species.name == "X. elegans"
        
        # Test unique constraint
        duplicate_species = Species(name="X. elegans")
        session.add(duplicate_species)
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()

    def test_gene_creation(self, session):
        """Test Gene model creation and relationships."""
        # Create species first
        species = Species(name="X. elegans")
        session.add(species)
        session.flush()  # Get the ID without committing
        
        # Create gene
        gene = Gene(
            gene_name="Xele.ptg000001l.104",
            species_id=species.id,
            coding_sequence="ATGCGATCGATCG"
        )
        session.add(gene)
        session.commit()
        
        assert gene.id is not None
        assert gene.gene_name == "Xele.ptg000001l.104"
        assert gene.species_id == species.id
        assert gene.coding_sequence == "ATGCGATCGATCG"
        
        # Test relationship
        assert gene.species == species
        assert gene in species.genes

    def test_annotation_creation(self, session):
        """Test Annotation model creation and relationships."""
        # Create prerequisites
        species = Species(name="X. elegans")
        session.add(species)
        session.flush()
        
        gene = Gene(gene_name="test_gene", species_id=species.id)
        session.add(gene)
        session.flush()
        
        # Create annotation
        annotation = Annotation(
            gene_id=gene.id,
            description="Test annotation",
            e_value=1e-10,
            similarity=95.5,
            bit_score=100.0,
            alignment_length=200,
            positives=190
        )
        session.add(annotation)
        session.commit()
        
        assert annotation.id is not None
        assert annotation.gene_id == gene.id
        assert annotation.description == "Test annotation"
        assert annotation.e_value == 1e-10
        assert annotation.similarity == 95.5
        
        # Test relationship
        assert annotation.gene == gene
        assert annotation in gene.annotations

    def test_go_annotation_relationship(self, session):
        """Test many-to-many relationship between Annotation and GO."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        annotation = Annotation(gene_id=gene.id)
        go_term = GO(go_id="GO:0003677", go_branch="F", go_name="DNA binding")
        
        session.add_all([species, gene, annotation, go_term])
        session.flush()
        
        # Create relationship
        annotation.go_ids.append(go_term)
        session.commit()
        
        # Test relationship
        assert go_term in annotation.go_ids
        assert annotation in go_term.annotations

    def test_arabidopsis_homologue_relationship(self, session):
        """Test many-to-many relationship between Gene and ArabidopsisHomologue."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        homologue = ArabidopsisHomologue(
            a_thaliana_locus="AT1G01010",
            a_thaliana_common_name="NAC domain protein"
        )
        
        session.add_all([species, gene, homologue])
        session.flush()
        
        # Create relationship
        gene.arabidopsis_homologues.append(homologue)
        session.commit()
        
        # Test relationship
        assert homologue in gene.arabidopsis_homologues
        assert gene in homologue.genes

    def test_regulatory_interaction(self, session):
        """Test RegulatoryInteraction model and relationships."""
        # Create prerequisites
        species = Species(name="X. elegans")
        regulator_gene = Gene(gene_name="regulator_gene", species_id=species.id)
        target_gene = Gene(gene_name="target_gene", species_id=species.id)
        
        session.add_all([species, regulator_gene, target_gene])
        session.flush()
        
        # Create regulatory interaction
        interaction = RegulatoryInteraction(
            regulator_gene_id=regulator_gene.id,
            target_gene_id=target_gene.id,
            regulatory_cluster="HSF:1",
            target_cluster="HD-ZIP:1",
            direction="Activation"
        )
        session.add(interaction)
        session.commit()
        
        assert interaction.id is not None
        assert interaction.regulator_gene_id == regulator_gene.id
        assert interaction.target_gene_id == target_gene.id
        assert interaction.direction == "Activation"
        
        # Test relationships
        assert interaction.regulator_gene == regulator_gene
        assert interaction.target_gene == target_gene
        assert interaction in regulator_gene.regulates_interactions
        assert interaction in target_gene.targeted_by_interactions

    def test_gene_expressions(self, session):
        """Test Gene_expressions model and relationships."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        experiment = Experiments(
            experiment_name="Test Experiment",
            description="Test description",
            species_id=species.id
        )
        
        session.add_all([species, gene, experiment])
        session.flush()
        
        # Create expression data
        expression = Gene_expressions(
            treatment="Control",
            time=0,
            replicate="Rep1",
            normalised_expression=1.5,
            log2_expression=0.58,
            experiment_id=experiment.id,
            species_id=species.id,
            gene_id=gene.id
        )
        session.add(expression)
        session.commit()
        
        assert expression.id is not None
        assert expression.treatment == "Control"
        assert expression.normalised_expression == 1.5
        
        # Test relationships
        assert expression.gene == gene
        assert expression.species == species
        assert expression.experiment == experiment

    def test_differential_expression(self, session):
        """Test DifferentialExpression model and relationships."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        experiment = Experiments(
            experiment_name="DE Test",
            species_id=species.id
        )
        
        session.add_all([species, gene, experiment])
        session.flush()
        
        # Create differential expression data
        de = DifferentialExpression(
            gene_id=gene.id,
            experiment_id=experiment.id,
            re_set="ReT04",
            re_direction="Up-regulated",
            de_set="DeT12",
            de_direction="Down-regulated"
        )
        session.add(de)
        session.commit()
        
        assert de.id is not None
        assert de.re_set == "ReT04"
        assert de.re_direction == "Up-regulated"
        
        # Test relationships
        assert de.gene == gene
        assert de.experiment == experiment

    def test_enzyme_code_annotation_relationship(self, session):
        """Test many-to-many relationship between Annotation and EnzymeCode."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        annotation = Annotation(gene_id=gene.id)
        enzyme = EnzymeCode(
            enzyme_code="EC:1.1.1.1",
            enzyme_name="Alcohol dehydrogenase"
        )
        
        session.add_all([species, gene, annotation, enzyme])
        session.flush()
        
        # Create relationship
        annotation.enzyme_codes.append(enzyme)
        session.commit()
        
        # Test relationship
        assert enzyme in annotation.enzyme_codes
        assert annotation in enzyme.annotations

    def test_interpro_annotation_relationship(self, session):
        """Test many-to-many relationship between Annotation and InterPro."""
        # Create prerequisites
        species = Species(name="X. elegans")
        gene = Gene(gene_name="test_gene", species_id=species.id)
        annotation = Annotation(gene_id=gene.id)
        interpro = InterPro(
            interpro_id="IPR000001",
            interpro_go_id="GO:0003677",
            interpro_go_name="DNA binding"
        )
        
        session.add_all([species, gene, annotation, interpro])
        session.flush()
        
        # Create relationship
        annotation.interpro_ids.append(interpro)
        session.commit()
        
        # Test relationship
        assert interpro in annotation.interpro_ids
        assert annotation in interpro.annotations

    def test_unique_constraints(self, session):
        """Test unique constraints in models."""
        # Test Species unique constraint
        species1 = Species(name="X. elegans")
        species2 = Species(name="X. elegans")
        session.add_all([species1, species2])
        
        with pytest.raises(Exception):
            session.commit()
        
        session.rollback()
        
        # Test Gene unique constraint
        species = Species(name="X. elegans")
        session.add(species)
        session.flush()
        
        gene1 = Gene(gene_name="test_gene", species_id=species.id)
        gene2 = Gene(gene_name="test_gene", species_id=species.id)
        session.add_all([gene1, gene2])
        
        with pytest.raises(Exception):
            session.commit()

    def test_cascade_deletes(self, session):
        """Test cascade delete behavior."""
        # Create a complete hierarchy
        species = Species(name="X. elegans")
        regulator = Gene(gene_name="regulator", species_id=species.id)
        target = Gene(gene_name="target", species_id=species.id)
        
        session.add_all([species, regulator, target])
        session.flush()
        
        interaction = RegulatoryInteraction(
            regulator_gene_id=regulator.id,
            target_gene_id=target.id,
            direction="Activation"
        )
        session.add(interaction)
        session.commit()
        
        # Delete the regulator gene
        session.delete(regulator)
        session.commit()
        
        # The interaction should be deleted due to cascade
        remaining_interactions = session.query(RegulatoryInteraction).all()
        assert len(remaining_interactions) == 0
"""
Defines all the data models used in the database
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, Float, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

'''
Association table for many to many relationship between annotations and GO ID terms
'''
annotations_go = Table(
    'annotations_go', Base.metadata,
    Column('annotation_id', Integer, ForeignKey('annotations.id'), primary_key=True),
    Column('go_id', Integer, ForeignKey('GO.id'), primary_key=True)
)

'''
Association table for many to many relationship between annotations and enzyme codes
'''
annotations_enzyme_codes = Table(
    'annotations_enzyme_codes', Base.metadata,
    Column('annotation_id', Integer, ForeignKey('annotations.id'), primary_key=True),
    Column('enzyme_code_id', Integer, ForeignKey('enzyme_codes.id'), primary_key=True)
)

'''
Association table for many to many relationship between annotations and interpro
'''
annotations_interpro = Table(
    'annotations_interpro', Base.metadata,
    Column('annotation_id', Integer, ForeignKey('annotations.id'), primary_key=True),
    Column('interpro_id', Integer, ForeignKey('interpro.id'), primary_key=True)
)

'''
Table for storing each of the different species (X. elegans, X. humilis, X. schlechteri)
'''

gene_homologue_association = Table(
     'gene_homologue_association', Base.metadata,
    Column('gene_id', Integer, ForeignKey('genes.id'), primary_key=True),
    Column('homologue_id', Integer, ForeignKey('arabidopsis_homologues.id'), primary_key=True)
)

class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    genes = relationship("Gene", back_populates="species")
    gene_expressions = relationship("Gene_expressions", back_populates="species")
    experiment = relationship("Experiments", back_populates="species")

class Gene(Base):
    __tablename__ = "genes"
    id  = Column(Integer, primary_key=True)
    gene_name = Column(String, nullable=False, unique=True)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    coding_sequence = Column(Text, nullable=True)

    species = relationship("Species", back_populates="genes")
    annotations = relationship("Annotation", back_populates="gene")
    arabidopsis_homologues = relationship('ArabidopsisHomologue',
                              secondary=gene_homologue_association,
                            back_populates='genes')
    gene_expressions = relationship("Gene_expressions", back_populates="genes")
    differential_expression = relationship("DifferentialExpression", back_populates="gene") 


class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('genes.id'), nullable=False)
    description = Column(Text, nullable=True)
    e_value = Column(Float, nullable=True)
    
    gene = relationship("Gene", back_populates="annotations") # creates a back reference to the gene table, so that we can access the gene object from the annotation object e.g annotation.gene
    
    # create many to many relationships with GO, EnzymeCode and InterPro tables
    # an (gene) annotation can be linked to many multiple GO terms, enzyme codes and InterPro IDs
    # and each GO term, enzyme code and InterPro ID can be linked to multiple annotations
    go_ids = relationship("GO", secondary=annotations_go, back_populates="annotations") 
    enzyme_codes = relationship("EnzymeCode", secondary=annotations_enzyme_codes, back_populates="annotations")
    interpro_ids = relationship("InterPro", secondary=annotations_interpro, back_populates="annotations")

class ArabidopsisHomologue(Base):
    __tablename__ = "arabidopsis_homologues"
    id = Column(Integer, primary_key=True)

    a_thaliana_locus = Column(String, nullable=True, unique=True)
    a_thaliana_common_name = Column(String, nullable=True)
    description = Column(Text, nullable=True, default="No Blast Hit")

    e_value = Column(Float, nullable=True)
    similarity = Column(Float, nullable=True)
    bit_score = Column(Float, nullable=True)
    alignment_length = Column(Integer, nullable=True)
    positives = Column(Integer, nullable=True)

    
    genes = relationship('Gene',
                         secondary=gene_homologue_association,
                        back_populates='arabidopsis_homologues')


# GO Table
class GO(Base):
    __tablename__ = 'GO'
    id = Column(Integer, primary_key=True)
    go_id = Column(String, nullable=False)
    go_branch = Column(CHAR, nullable=True) # either (C)ellular Component, Molecular (F)unction or Biological (P)rocess
    go_name = Column(String, nullable=True)

    annotations = relationship("Annotation", secondary=annotations_go, back_populates="go_ids")

# Enzyme Codes Table
class EnzymeCode(Base):
    __tablename__ = 'enzyme_codes'
    id = Column(Integer, primary_key=True)
    enzyme_code = Column(String, nullable=False)
    enzyme_name = Column(String, nullable=True)

    annotations = relationship("Annotation", secondary=annotations_enzyme_codes, back_populates="enzyme_codes")

# InterPro Table
class InterPro(Base):
    __tablename__ = 'interpro'
    id = Column(Integer, primary_key=True)
    interpro_id = Column(String, nullable=False)
    interpro_go_id = Column(String, nullable=True)
    interpro_go_name = Column(String, nullable=True)

    annotations = relationship("Annotation", secondary=annotations_interpro, back_populates="interpro_ids")

class Gene_expressions(Base):
    __tablename__ = "gene_expressions"

    id = Column(Integer, primary_key=True)
    treatment = Column("treatment", String, nullable=False)
    time = Column("time", Integer, nullable=False)
    replicate = Column("replicate", String, nullable=False)
    normalised_expression = Column("normalised_expression", Float, nullable=False)
    log2_expression = Column("log2_expression", Float,nullable=False)
    meta_data = Column("meta_data", Text, nullable=True)

    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    gene_id = Column(Integer, ForeignKey("genes.id"), nullable=False)

    experiment = relationship("Experiments", back_populates="gene_expressions")
    species = relationship("Species", back_populates="gene_expressions")
    genes = relationship("Gene", back_populates="gene_expressions")

class Experiments(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    experiment_name = Column("experiment_name", String)
    description = Column("description", Text, nullable=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=True)  # Foreign key linking to Species

    gene_expressions = relationship("Gene_expressions", back_populates="experiment")
    species = relationship("Species", back_populates="experiment")
    differential_expression = relationship("DifferentialExpression", back_populates="experiment")

class DifferentialExpression(Base):
    __tablename__ = "differential_expression"

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey("genes.id"), nullable=False)  # Links to Gene
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)  # Links to Experiment
    re_set = Column(String, nullable=True)  # Earliest Rehydration time point (e.g., "ReT04")
    re_direction = Column(String, nullable=True)  # Direction in Re ("Up-regulated"/"Down-regulated")
    de_set = Column(String, nullable=True)  # Earliest Dehydration time point (e.g., "DeT12")
    de_direction = Column(String, nullable=True)  # Direction in De ("Up-regulated"/"Down-regulated")

    # Relationships
    gene = relationship("Gene", back_populates="differential_expression")
    experiment = relationship("Experiments", back_populates="differential_expression")
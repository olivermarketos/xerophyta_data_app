"""
Defines all the data models used in the database
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

xe_gene_homologue_link = Table(
    'xe_gene_homologue_link', Base.metadata,
    Column('gene_name', String, ForeignKey('gene_info.gene_name')),
    Column('arabidopsis_id', Integer, ForeignKey('arabidopsis_homologues.arabidopsis_id'))
)


class Gene_expressions(Base):
    __tablename__ = "gene_expressions"

    id = Column("id",String, primary_key=True)
    gene_name = Column("gene_name", String, ForeignKey('gene_info.gene_name'))
    treatment_time = Column("treatment_time", Integer)
    experiment_time = Column("experiment_time", Integer)
    normalised_expression = Column("normalised_expression", Float)
    log2_expression = Column("log2_expression", Float)
    species = Column("species", String)
    treatment = Column("treatment", String)
    replicate = Column("replicate", Integer)



class Gene_info(Base):
    __tablename__ = 'gene_info'
    gene_name = Column(String, primary_key=True)


    sequence_description = Column(Text, nullable=True)
    blast_min_e_value = Column(Float, nullable=True)
    nt_sequence = Column(Text, nullable=True)
    Hit_desc = Column(Text)
    Hit_ACC = Column(String)
    Similarity= Column("Similarity", Float)
    Bit_Score= Column("Bit_Score", Float)
    Alignment_length= Column("Alignment_length",Integer)
    Positives= Column("Positives",Integer)
    
    differentially_expressed = Column(Boolean, nullable=True)

    uniprot_id = Column(String)

    # arabidopsis_gene_names = relationship("ArabidopsisGeneNames", back_populates="gene_info")
    # arabidopsis_gene_loci = relationship("ArabidopsisGeneLoci", back_populates="gene_info")

    # homologues = relationship('Arabidopsis_Homologue', secondary=xe_gene_homologue_link, back_populates='gene_info')

class Arabidopsis_homologue(Base):
    __tablename__ = 'arabidopsis_homologues'
    arabidopsis_id = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String, unique=True, nullable=True)
    at_locus = Column(String, nullable=True)
    
    # Many-to-many relationship with Xe genes
    gene_info = relationship('Gene_info', secondary=xe_gene_homologue_link, back_populates='homologues')

    # One-to-many relationship with common names
    common_names = relationship('AtCommonName', back_populates='homologue')

class AtCommonName(Base):
    __tablename__ = 'At_common_names'
    common_name_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    arabidopsis_id = Column(Integer, ForeignKey('arabidopsis_homologues.arabidopsis_id'))
    
    homologue = relationship('ArabidopsisHomologue', back_populates='At_common_names')

# class GO_terms(Base):
#     __tablename__ = 'go_terms'
#     go_id = Column(String, primary_key=True)
#     go_name = Column(String)
#     go_category = Column(String)

# class Gene_to_GO(Base):
#     __tablename__ = 'gene_to_go'

#     gene_name = Column(String, ForeignKey('gene_info.gene_name') )
#     go_id = Column(String,ForeignKey('go_terms.go_id'))

# class Enzymes(Base):
#     __tablename__ = 'enzymes'
#     enzyme_code = Column(String, primary_key=True)
#     enzyme_name = Column(String)

# class Gene_to_enzyme(Base):
#     __tablename__ = 'gene_to_enzyme'

#     gene_name = Column(String, ForeignKey('gene_info.gene_name') )
#     enzyme_code = Column(String,ForeignKey('enzymes.enzyme_code'))

# class InterPro(Base):
#     __tablename__ = "interpro"
#     interpro_id = Column(String, primary_key=True)
#     interpro_name = Column(String)

# class Gene_to_interpro(Base):
#     __tablename__ = 'gene_to_interpro'

#     gene_name = Column(String, ForeignKey('gene_info.gene_name') )
#     interpro_id = Column(String,ForeignKey('interpro.interpro_id'))


# class ArabidopsisGeneNames(Base):
#     __tablename__ = 'At_gene_names'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     gene_name = Column(String, ForeignKey('gene_info.gene_name'))
#     at_gene_name = Column(String, nullable=False)

#     # Relationship to the gene_info table
#     gene_info = relationship("Gene_info", back_populates="At_gene_names")

# class ArabidopsisGeneLoci(Base):
#     __tablename__ = 'At_gene_loci'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     gene_name = Column(String, ForeignKey('gene_info.gene_name'))
#     at_gene_loci = Column(String)

#     # Relationship to the gene_info table
#     gene_info = relationship("Gene_info", back_populates="At_gene_loci")
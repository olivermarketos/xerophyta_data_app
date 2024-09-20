"""
Defines all the data models used in the database
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

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

    # def __init__(self, g_name, t_time, exp_time, norm_exp,log_exp, species, treatment, rep ):
    #     self.gene_name = g_name
    #     self.treatment_time = t_time
    #     self.experiment_time = exp_time
    #     self.normalised_expression = norm_exp
    #     self.log2_expression = log_exp
    #     self.species = species
    #     self.treatment = treatment
    #     self.replicate = rep


    # def __repr__(self):
    #     return(f"{self.gene_name} {self.log2_expression} {self.experiment_time}")


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
    At_gene_name = Column(String)
    At_locus_id = Column(String)
    # protein = Column(String, nullable=True)
    # blast_taxonomy = Column(String, nullable=True)
    # annotation_GO_ID = Column(String, nullable=True)
    # annotation_GO_term = Column(String, nullable=True)
    # enzyme_code = Column(String, nullable=True)
    # enzyme_name = Column(String, nullable=True)
    # interPro_accession = Column(String, nullable=True)
    # interPro_name = Column(String, nullable=True)
    
    # aa_sequence = Column(Text, nullable=True)

    # arabidopsis_homolog = Column(String, nullable=True)
    # Sequence_length

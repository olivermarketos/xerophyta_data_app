"""
Helper file for various database tasks, like creating and loading data.

Accepted command-line arguments:
    create_db
    add_users
    add_chats
    add_messages
    get_messages
    add_user
    start_chat

"""

import argparse
import re
import models
import os
import sqlalchemy as sq
import db as db
import pandas as pd
import uuid
from Bio import SeqIO

DATABASE_NAME = "xerophyta_db.sqlite"

def create_new_db():
    """
    Deletes and recreates the SQLITE database. Is required when the model structure changes
    """
    print("Deleting old database file...")

    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        
    print("Creating new db")
    engine = sq.create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
    connection = engine.connect()

    print("Creating tables")
    models.Base.metadata.create_all(engine)

    print("DONE")

def add_rna_seq():
    """
    Populates the database with dummy user data from an excel file
    """
    database = db.DB()
    data = pd.read_csv("data/Xe_seedlings_normalised_counts_tidy.csv")
    data['id'] = data["id"]+'_'+data['gene_name']

    database.batch_create_or_update(models.Gene_expressions, data.to_dict("records"), "id")

def add_gene_names():
    database = db.DB()
    data = pd.read_csv("data/Xe_seedlings_normalised_counts_tidy.csv")
    gene_names = pd.unique((data["gene_name"]))

    records = [{"gene_name": gene_name} for gene_name in gene_names]
    database.batch_create_or_update(models.Gene_info, records, "gene_name")

def add_gene_nuc_seq():
    database = db.DB()

    records =[{"gene_name": seq_record.id, "nt_sequence": str(seq_record.seq)} for seq_record in SeqIO.parse("data/Xelegans_CDS_annot150424.fasta", "fasta")]

    database.batch_create_or_update(models.Gene_info, records, "gene_name")

def add_annotation_data():
    database = db.DB()
    # df = pd.read_csv("data/20240918_ALL_topblast_blastx.csv")
    df = pd.read_csv("data/20240918_Arabidopsis_topblast_blastx.csv")
    df = df.rename(columns={'Sequence name':'gene_name',
                            'Sequence desc.':'sequence_description',
                            'Hit desc.':'Hit_desc',
                            'Hit ACC':'Hit_ACC',
                            'E-Value':'blast_min_e_value',
                            'Bit-Score':'Bit_Score',
                            'Alignment length':'Alignment_length',
                            })
    df = df.drop('Sequence length', axis=1)
    print(df.head())

    database.batch_create_or_update(models.Gene_info, df.to_dict("records"), "gene_name")

def get_expression():
    """
    Fetches all expression values from the database based on a gene name
    """
    gene_name = input("Gene name:")

    database = db.DB()
    time = []
    treatment_time = []
    print()
    for i, value in enumerate(database.get_expression_by_gene_name(gene_name)):
        time.append(value.experiment_time)
        treatment_time.append(value.treatment_time)
    print(time)
    print(treatment_time)

def add_uniprot_id_mapping():

    database = db.DB()
    print("Reading in data...")
    df = pd.read_csv("data/uniprot/arab_idmapping_2024_09_22.csv")
    
    print("Done.\nRefactoring data...")

    df = df.rename(columns={'Entry':'Hit_ACC',        
                            'Gene Names':'At_gene_name'
                            })
    
    df = df[['Hit_ACC',"At_gene_name"]]
    df['At_gene_name'] = df['At_gene_name'].astype(str)
    df['At_locus_id'] = df['At_gene_name'].apply(extract_arabidopsis_locus)

    df['At_gene_name'] = df["At_gene_name"].apply(remove_arabidopsis_locus)
    # database.batch_create_or_update(models.Gene_info, df.to_dict("records"), "Hit_ACC")
    print("Done.\nAdding to database...")

    database.add_gene_locus(models.Gene_info, df.to_dict("records"))
    print("Done.")


def remove_arabidopsis_locus(gene_name):
    return re.sub(r'At[1-5]g\d{5}', '', gene_name).strip()  # Remove the locus and strip any extra spaces


def extract_arabidopsis_locus(gene_name):
    match = re.search(r'At[1-5]g\d{5}', gene_name)
    if match:
        return match.group(0)  # Return the matched locus
    else:
        return None  # Return None if no locus is found

        

def init_db():
    create_new_db()
    add_gene_nuc_seq()
    # add_gene_names()
    add_rna_seq()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("command")
    
    args = parser.parse_args()
   
    if args.command == "create_db":
        create_new_db()

    elif args.command == "add_rna_seq":
       add_rna_seq()


    elif args.command == "get_expression":
        get_expression()

  
    elif args.command == "init":
        init_db()

    elif args.command == "get_chats":
        users = input("Users: ").split()
        d = db.DB()

        chat = d.get_or_create_chat(users)

        print(chat.chat_id)

    elif args.command == "add_genes":
        add_gene_names()

    elif args.command == "add_seq":
        add_gene_nuc_seq()

    elif args.command == "add_gene_info":
        add_annotation_data()
    
    elif args.command == "add_uniprot":
        add_uniprot_id_mapping()
    else:
        print("Unrecognized command")

    pass

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
    data = pd.read_csv("data/Xelegans_ALL_Arabidopsis_annotation_topblast.csv")
    print(data.head())
    database.batch_create_or_update(models.Gene_info, data.to_dict("records"), "gene_name")

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


def add_user():
    """
    Either inserts or updates a user in the database
    """
    database = db.DB()

    id = input("ID: ")
    first_name = input("Name: ")
    last_name = input("Last Name: ")
    ip_address = input("IP: ")

    print(database.create_or_update(models.User, [{
        "user_id": id,
        "first_name": first_name, 
        "last_name": last_name,
        "ip_address": ip_address
    }], "user_id"))


def start_chat():
    """
    Creates a new chat in the database
    """
    users = input("Enter list of users separated by a space: ").split(" ")
    
    print(users)
    
    d = db.DB()

    new_chat = d.create_or_update(models.Chat, [{"chat_id": str(uuid.uuid4())}], "chat_id")
    
    users = d.get_users(users)
   

    for user in users:
        new_chat.users.append(user)

    d.session.commit()
        

def init_db():
    create_new_db()
    add_gene_names()
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

    elif args.command == "add_user":
        add_user()
    
    elif args.command == "start_chat":
        start_chat()

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
    else:
        print("Unrecognized command")

    pass

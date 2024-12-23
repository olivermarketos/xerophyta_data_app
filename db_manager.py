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
import models as models
import os
import sqlalchemy as sq
import db as db
import pandas as pd
import uuid
from Bio import SeqIO

# DATABASE_NAME = "xerophyta_db.sqlite"
# DATABASE_NAME = "test_db.sqlite"
DATABASE_NAME = "all_xerophyta_species_db.sqlite"


####################
# Functions used for creating and populating the current database "all_xerophyta_species_db.sqlite""
####################
def create_new_db():
    """
    Deletes and recreates the SQLITE database. Is required when the model structure changes
    """

    if os.path.exists(DATABASE_NAME):
        print("Deleting old database file...")
        os.remove(DATABASE_NAME)
        
    print("Creating new db")
    engine = sq.create_engine(f"sqlite:///{DATABASE_NAME}", echo=False)
    connection = engine.connect()

    print("Creating tables")
    models.Base.metadata.create_all(engine)

    print("DONE")

def add_gene_sequence_from_fasta(filename, species_id):
    database = db.DB()
    species_name = database.session.query(models.Species).filter_by(id=species_id).first().name
    print(f"Adding gene sequences for {species_name} from {filename}")
    with open(filename, "r") as f:
        records = [{  "gene_name": seq_record.id, 
                      "species_id": species_id,
                      "coding_sequence": str(seq_record.seq)} 
                      for seq_record in SeqIO.parse(f, "fasta")]
    database.create_or_update(models.Gene, records, "gene_name")
    print("Done")

def parse_annotations(filename):
    df = pd.read_csv(filename)

     # Split columns with lists (GO IDs, GO Names, etc.)
    df["GO IDs"] = df["GO IDs"].str.split("; ")
    df["GO Names"] = df["GO Names"].str.split("; ")
   # Use .apply() to fill missing values with empty lists
    df["Enzyme Codes"] = df["Enzyme Codes"].str.split("; ").apply(lambda x: x if isinstance(x, list) else [])
    df["Enzyme Names"] = df["Enzyme Names"].str.split("; ").apply(lambda x: x if isinstance(x, list) else [])
    df["InterPro IDs"] = df["InterPro IDs"].str.split("; ").apply(lambda x: x if isinstance(x, list) else [])

    df.to_csv("output.csv", index=False)

    return df 

def map_genes_to_ids(species_id):
    # used for retrieving associated gene ids in the database from gene names (eg gene name Xe10001.1 is gene ID 1 in database)
    database = db.DB()
    gene_dict = {}
    genes = database.session.query(models.Gene).filter_by(species_id=species_id).all()
    
    for gene in genes:
        gene_dict[gene.gene_name] = gene.id
    return gene_dict

def add_gene_annotations(filename, species_id):
    database = db.DB()
    annotations_df = parse_annotations(filename)
    gene_dict = map_genes_to_ids(species_id)

    for _, row in annotations_df.iterrows():
        
        # map SeqName to gene_id
        gene_id = gene_dict.get(row["SeqName"])
        if not gene_id:
            print(f"Gene {row['SeqName']} not found in database")
            continue

        annotation_data = {
            "gene_id": gene_id,
            "description": row["Description"],
            "e_value": row["e-Value"],
        }
        # populate the annotation table
        # TODO this is slow, consider batching
        annotation_instance = database.create_or_update(models.Annotation, [annotation_data], lookup_field= "gene_id")

        go_terms = zip(row["GO IDs"], row["GO Names"])
        for go_id, go_name in go_terms:
            go_data = {
                "go_id": go_id,
                "go_branch": go_id.split(":")[0],  # Extract branch (P, F, or C)
                "go_name": go_name
            }
            go_instance = database.create_or_update(models.GO, [go_data], lookup_field="go_id")
            if go_instance not in annotation_instance.go_ids:
                annotation_instance.go_ids.append(go_instance)

        # Add Enzyme Codes
        enzyme_codes = zip(row["Enzyme Codes"], row["Enzyme Names"])
        for enzyme_code, enzyme_name in enzyme_codes:
            enzyme_data = {
                "enzyme_code": enzyme_code,
                "enzyme_name": enzyme_name
            }
            enzyme_instance = database.create_or_update(models.EnzymeCode, [enzyme_data], lookup_field="enzyme_code")
            if enzyme_instance not in annotation_instance.enzyme_codes:
                annotation_instance.enzyme_codes.append(enzyme_instance)

        # Add InterPro IDs
        for interpro_id in row["InterPro IDs"]:
            interpro_data = {
                "interpro_id": interpro_id
            }
            interpro_instance = database.create_or_update(models.InterPro, [interpro_data], lookup_field="interpro_id")
            if interpro_instance not in annotation_instance.interpro_ids:
                annotation_instance.interpro_ids.append(interpro_instance)

    # Commit all changes at the end
    database.session.commit()

def main(species_name, fasta_file, annotation_file, homologue_file):
    database = db.DB()
    species = database.add_species(species_name) # add species to database
    species_id = species.id
    add_gene_sequence_from_fasta(fasta_file, species_id) # add gene sequences to database from fasta file
    add_gene_annotations( annotation_file, species_id) # add gene annotations to database

if __name__ == "__main__":
    # replace  the following with the appropriate file paths and values
    species_name = "X. schlechteri"
    fasta_file = "all_data/Xschlechteri_Nov2024/Xsch_CDS_annot150424.fasta"
    annotation_file = "all_data/Xschlechteri_Nov2024/20241108_Xschlechteri_annotation_23009_export_table_Oliver.csv"
    homologue_file = "data/uniprot/arab_idmapping_2024_09_22.csv"
    main(species_name, fasta_file, annotation_file, homologue_file)
####################
# Older functons used for previous versions of the database
####################


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




def add_at_homologues():

    database = db.DB()
    print("Reading in data...")
    df = pd.read_csv("data/uniprot/arab_idmapping_2024_09_22.csv")
    
    print("Done.\nRefactoring data...")

    df = df.rename(columns={'Entry':'acc_num',        
                            'Gene Names':'At_gene_name'
                            })
    
    df = df[['acc_num',"At_gene_name"]]
    print(df)
    df['At_gene_name'] = df['At_gene_name'].astype(str)

    df['at_locus'] = df['At_gene_name'].apply(extract_arabidopsis_locus)
    df['common_name'] = df['At_gene_name'].astype(str)

    df['common_name'] = df["common_name"].apply(extract_common_names)
    print("Done.\nAdding to database...")

    for _, row in df.iterrows():
        # Call the database method for each row
        database.add_at_homologues(
            acc_num=row['acc_num'],
            at_locus=row['at_locus'],
            common_name_list=row['common_name']
        )


def extract_common_names(gene_name):
    extracted_names = []  # List to store the extracted names
    at_locus_pattern = r"(At\d{1}g\d{5}|AtCg\d{5})"

    match = re.search(at_locus_pattern, gene_name)

    if match:
        # Extract everything to the left of the matched Arabidopsis locus
        left_part = gene_name[:match.start()].strip()
        extracted_names=left_part.split()
          # Add the extracted part to the list
    return extracted_names


def extract_arabidopsis_locus(gene_name):
    match = re.search(r'At[1-5]g\d{5}', gene_name)
    if match:
        return match.group(0)  # Return the matched locus
    else:
        return None  # Return None if no locus is found

        

    


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()

#     parser.add_argument("command")
    
#     args = parser.parse_args()
   
#     if args.command == "create_db":
#         create_new_db()

#     elif args.command == "add_rna_seq":
#        add_rna_seq()


#     elif args.command == "get_expression":
#         get_expression()

  
#     elif args.command == "init":
#         init_db()

#     elif args.command == "get_chats":
#         users = input("Users: ").split()
#         d = db.DB()


#         print(chat.chat_id)

#     elif args.command == "add_genes":
#         add_gene_names()

#     elif args.command == "add_seq":
#         add_gene_nuc_seq()

#     elif args.command == "add_gene_info":
#         add_annotation_data()
    
#     elif args.command == "add_homologues":
#         add_at_homologues()
#     else:
#         print("Unrecognized command")

#     pass

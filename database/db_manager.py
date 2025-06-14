import re
from Bio import SeqIO
import database.models as models
import os
import sqlalchemy as sq
import database.db as db
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
import tqdm as tqdm

# DATABASE_NAME = "xerophyta_db.sqlite"
# DATABASE_NAME = "test_db.sqlite"
DATABASE_NAME = "database/data/all_xerophyta_species_db.sqlite"


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
    database.create_or_update(models.Gene, records, ["gene_name"])
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
        annotation_instance = database.create_or_update(models.Annotation, [annotation_data], lookup_fields= ["gene_id"])

        go_terms = zip(row["GO IDs"], row["GO Names"])
        for go_id, go_name in go_terms:
            go_data = {
                "go_id": go_id,
                "go_branch": go_id.split(":")[0],  # Extract branch (P, F, or C)
                "go_name": go_name
            }
            go_instance = database.create_or_update(models.GO, [go_data], lookup_fields=["go_id"])
            if go_instance not in annotation_instance.go_ids:
                annotation_instance.go_ids.append(go_instance)

        # Add Enzyme Codes
        enzyme_codes = zip(row["Enzyme Codes"], row["Enzyme Names"])
        for enzyme_code, enzyme_name in enzyme_codes:
            enzyme_data = {
                "enzyme_code": enzyme_code,
                "enzyme_name": enzyme_name
            }
            enzyme_instance = database.create_or_update(models.EnzymeCode, [enzyme_data], lookup_fields=["enzyme_code"])
            if enzyme_instance not in annotation_instance.enzyme_codes:
                annotation_instance.enzyme_codes.append(enzyme_instance)

        # Add InterPro IDs
        for interpro_id in row["InterPro IDs"]:
            interpro_data = {
                "interpro_id": interpro_id
            }
            interpro_instance = database.create_or_update(models.InterPro, [interpro_data], lookup_fields=["interpro_id"])
            if interpro_instance not in annotation_instance.interpro_ids:
                annotation_instance.interpro_ids.append(interpro_instance)

    # Commit all changes at the end
    database.session.commit()

def add_experiment(experiment_name, description= None):
    database = db.DB()
    experiment = database.create_or_update(models.Experiments, [{"experiment_name": experiment_name, "description": description}], ["experiment_name"])
    return experiment

def add_rna_seq_data(df, species, experiment_name):
    database = db.DB()
    lookup_field = ["gene_id","treatment","time","replicate"]

    species_id = database.session.query(models.Species.id).filter( models.Species.name == species ).scalar()
    experiment_id = database.session.query(models.Experiments.id).filter( models.Experiments.experiment_name == experiment_name ).scalar()
    
    if species_id is None:
        raise ValueError(f"Species '{species}' not found in the database")
    if experiment_id is None:
        raise ValueError(f"Experiment '{experiment_name}' not found in the database")
    
    
    records = []
    for _, row in df.iterrows():
        gene_id = database.session.query(models.Gene.id).filter(models.Gene.gene_name == row["gene_name"]).scalar()
        if gene_id:
            record = {
                "treatment": row["treatment"],
                "time": int(row["time"]),
                "replicate": (row["replicate"]),
                "normalised_expression": float(row["normalised_expression"]),
                "log2_expression": float(row["log2_expression"]),
                "meta_data": None,
                "experiment_id": experiment_id,
                "species_id": species_id,
                "gene_id": gene_id
            }
            records.append(record)
        else:
            raise ValueError(f"Gene {row['gene_name']} not found in database")
    
        
    database.create_or_update(models.Gene_expressions, records, lookup_fields= lookup_field)

def add_DEG_data(file_name, experiment_name):
    database = db.DB()
    data = pd.read_csv(file_name)
    
    # Ensure columns exist
    required_columns = ["Genes", "Re_Set", "Re_direction", "De_Set", "De_direction"]
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"CSV is missing one or more required columns: {required_columns}")

    # Fetch the experiment ID
    experiment = database.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found in the database.")
    experiment_id = experiment.id

    records = []  

    for _, row in data.iterrows():
        gene_name = row["Genes"]

        # Fetch the gene ID
        gene = database.get_gene_by_name(gene_name)
        if gene is None:
            print(f"Gene '{gene_name}' not found in the database. Skipping...")
            continue
        gene_id = gene.id

        # Prepare record
        record = {
            "gene_id": gene_id,
            "experiment_id": experiment_id,
            "re_set": row["Re_Set"] if row["Re_Set"] != "None" else None,
            "re_direction": row["Re_direction"] if row["Re_direction"] != "None" else None,
            "de_set": row["De_Set"] if row["De_Set"] != "None" else None,
            "de_direction": row["De_direction"] if row["De_direction"] != "None" else None,
        }
        records.append(record)

    # Use the create_or_update function to add or update records
    if records:
        database.create_or_update(models.DifferentialExpression, records, lookup_fields=["gene_id", "experiment_id"])
        print(f"Processed {len(records)} records.")
    else:
        print("No records to process.")
    
def add_a_thaliana_gene_mapping(mapping_file):
    database = db.DB()
    
    data = pd.read_csv(mapping_file)
    
    # Ensure columns exist
    required_columns = ["Gene name","At Locus ID","Wiki gene description"]
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"CSV is missing one or more required columns: {required_columns}")

    data.sort_values("At Locus ID", inplace=True, ascending=False)

    database.add_a_thaliana_gene_mappings(data)

def add_regulatory_interactions(grn_data_df, species_name=None):
    """
    Adds gene regulatory network interactions to the database.

    Args:
        grn_data_df (pd.DataFrame): DataFrame with GRN data.
        Expected columns: "Regulatory cluster", "Predicted regulators",
                                "Target cluster", "Predicted targets", "Direction of regulation"
        species_name (str, optional): If provided, interactions will only be added if
                                        both regulator and target genes belong to this species.
                                        This can be useful if gene names are not globally unique
                                        across species in your `genes` table (though your current
                                        `gene_name` is unique).
    """
    database = db.DB()

    required_columns = [
        "Regulatory cluster", "Predicted regulators",
        "Target cluster", "Predicted targets", "Direction of regulation"
    ]
    if not all(col in grn_data_df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in grn_data_df.columns]
        raise ValueError(f"GRN DataFrame is missing required columns: {missing_cols}")

    interactions_added = 0
    interactions_skipped_gene_not_found = 0
    genes_not_found = set()  # To track unique genes not found
    interactions_skipped_species_mismatch = 0
    interactions_skipped_already_exists = 0
    
    target_species_id = None
    if species_name:
        species_obj = database.get_species_by_name(species_name)
        if not species_obj:
            print(f"Warning: Species '{species_name}' not found. Cannot filter by species.")
        else:
            target_species_id = species_obj.id

    for index, row in tqdm.tqdm(grn_data_df.iterrows(), total=len(grn_data_df), desc="Processing GRN interactions"):
        regulator_gene_name = row["Predicted regulators"]
        target_gene_name = row["Predicted targets"]
        regulatory_cluster = row["Regulatory cluster"]
        target_cluster = row["Target cluster"]
        direction = row["Direction of regulation"] # e.g., "Activation"

        # 1. Find the regulator Gene object
        regulator_gene = database.session.query(models.Gene).filter_by(gene_name=regulator_gene_name).first()
        if not regulator_gene:
            print(f"Warning: Regulator gene '{regulator_gene_name}' not found. Skipping interaction row {index+1}.")
            interactions_skipped_gene_not_found += 1
            genes_not_found.add(regulator_gene_name)  # Track unique gene not found
            continue

        # 2. Find the target Gene object
        target_gene = database.session.query(models.Gene).filter_by(gene_name=target_gene_name).first()
        if not target_gene:
            print(f"Warning: Target gene '{target_gene_name}' not found. Skipping interaction row {index+1}.")
            interactions_skipped_gene_not_found += 1
            genes_not_found.add(target_gene_name)  # Track unique gene not found
            continue
        
        # 3. (Optional) Check if genes belong to the specified species
        if target_species_id is not None:
            if getattr(regulator_gene, "species_id", None) != target_species_id or \
                getattr(target_gene, "species_id", None) != target_species_id:
                print(f"Warning: Regulator '{regulator_gene_name}' (species {regulator_gene.species_id}) or "
                        f"target '{target_gene_name}' (species {target_gene.species_id}) "
                        f"does not belong to target species {target_species_id}. Skipping interaction row {index+1}.")
                interactions_skipped_species_mismatch += 1
                continue

        # 4. Check if this interaction already exists (using the UniqueConstraint)
        existing_interaction = (
            database.session.query(models.RegulatoryInteraction)
            .filter_by(
                regulator_gene_id=regulator_gene.id,
                target_gene_id=target_gene.id
                # You might add other fields here if your UniqueConstraint is more complex
                # e.g., experiment_id if you add that to RegulatoryInteraction
            )
            .first()
        )

        if existing_interaction:
            # Optionally update if direction or clusters changed, or just skip
            # For now, we'll skip if it exists to avoid duplicates.
            # You could add logic here to update `direction`, `regulatory_cluster`, `target_cluster`
            # if `existing_interaction.direction != direction` etc.
            # print(f"Interaction between {regulator_gene_name} and {target_gene_name} already exists. Skipping row {index+1}.")
            interactions_skipped_already_exists += 1
            continue

        # 5. Create and add the new RegulatoryInteraction
        try:
            new_interaction = models.RegulatoryInteraction(
                regulator_gene_id=regulator_gene.id,  # or regulator_gene=regulator_gene
                target_gene_id=target_gene.id,        # or target_gene=target_gene
                regulatory_cluster=regulatory_cluster,
                target_cluster=target_cluster,
                direction=direction  # This must match one of your Enum values ('Activation', 'Repression', 'Unknown')
            )
            database.session.add(new_interaction)
            interactions_added += 1
        except ValueError as ve: # Catches issues if `direction` is not in Enum
            print(f"Error creating interaction for row {index+1}: {ve}. Invalid direction value: '{direction}'. Skipping.")
            database.session.rollback() # Rollback the add attempt for this interaction
            continue


        # Commit in batches for performance
        if (index + 1) % 1000 == 0:
            try:
                database.session.commit()
                # print(f"Committed {interactions_added} new interactions so far (processed {index + 1} rows).")
            except SQLAlchemyError as e:
                database.session.rollback()
                print(f"Error committing batch: {e}")
                # Potentially stop or handle more gracefully
                raise

    # Final commit for any remaining interactions
    try:
        database.session.commit()
    except SQLAlchemyError as e:
        database.session.rollback()
        print(f"Error during final commit: {e}")
        raise
        
    print(f"\n--- GRN Population Summary ---")
    print(f"Successfully added: {interactions_added} interactions.")
    print(f"Skipped (gene not found): {interactions_skipped_gene_not_found} interactions.")
    if species_name:
        print(f"Skipped (species mismatch): {interactions_skipped_species_mismatch} interactions.")
    print(f"Skipped (already exists): {interactions_skipped_already_exists} interactions.")
    print(f"Total rows processed: {len(grn_data_df)}")

    print(f"Unique genes not found in DB: {len(genes_not_found)}")



def main(species_name, fasta_file, annotation_file, homologue_file):
    database = db.DB()
    species = database.add_species(species_name) # add species to database
    species_id = species.id
    add_gene_sequence_from_fasta(fasta_file, species_id) # add gene sequences to database from fasta file
    add_gene_annotations( annotation_file, species_id) # add gene annotations to database

if __name__ == "__main__":
    # replace  the following with the appropriate file paths and values
    # species_name = "X. elegans"
    # experiment_name = "xe_seedlings_time_course"
    # fasta_file = "all_data/Xschlechteri_Nov2024/Xsch_CDS_annot150424.fasta"
    # annotation_file = "all_data/Xschlechteri_Nov2024/20241108_Xschlechteri_annotation_23009_export_table_Oliver.csv"
    # homologue_file = "data/uniprot/arab_idmapping_2024_09_22.csv"
    # # main(species_name, fasta_file, annotation_file, homologue_file)

    # # rna_seq_data = pd.read_csv("all_data/Michael_RNAseq/Xe_seedlings (updated)/Xe_seedlings_DESeq2_normalised_counts_table_tidy_for_db.csv")
    # # add_rna_seq_data(rna_seq_data, species_name, experiment_name) # add rna seq data to database

    # DEG_data = "all_data/Michael_RNAseq/Xe_seedlings (updated)/All genes with earliest onset of DE with direction.csv"
    # experiment_name = "xe_seedlings_time_course"

    # add_DEG_data(DEG_data, experiment_name) # add DEG data to database

    file = "all_data/test_grn.csv"
    df = pd.read_csv(file)
    add_regulatory_interactions(df, species_name="X. elegans")

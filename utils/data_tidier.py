import pandas as pd
import numpy as np


def transform_to_long(df):
    '''
    Data: dataframe contating the gene expression data
        Expects the header to be in the format:
            "Species_Treatment_Replicate_Time" 
            e.g "Xe_De_R2_T03", etc.
    '''
    # Parse the header and split it into columns
    header = df.columns.tolist()
    parsed_columns = []

    # Expects the header to be in the format "Species_Treatment_Replicate_Time" e.g "Xe_De_R2_T03", etc.
    for col in header[1:]:  # Skip the first gene column
        # Extract the species, treatment, replicate, and time
        parts = col.split("_")
        
        species = parts[0]  # e.g., "Xe"
        if species == "Xe":
            species = "X. elegans"
        elif species == "Xs":
            species = "X. schlechteri"
        elif species == "Xh":
            species = "X. humilis"
        else:
            raise ValueError(f"Unknown species: {species}. Expected 'Xe', 'Xs', or 'Xh'.")
        
        treatment = parts[1]  # e.g., "De" or "Re"
        replicate = parts[2]  # e.g., "R2", "R3", etc.
        time = parts[3]  # e.g., "T00", "T03", etc.
        parsed_columns.append((species, treatment, replicate, time))

    # Create a long-form DataFrame for database insertion
    data = []
    for index, row in df.iterrows():
        gene_name = row[0]  # First column is the gene name
        for col, (species, treatment, replicate, time) in zip(header[1:], parsed_columns):
            expression = row[col]
            data.append({
                "gene_name": gene_name,
                "species": species,
                "treatment": treatment,
                "replicate": replicate,
                "time": time,
                "expression": expression
            })

    # Convert to DataFrame
    long_df = pd.DataFrame(data)

    return long_df

 
def add_log2(df):
    df["log2_expression"] = np.log2(df['expression']+1)
    return df

def calculate_experiment_time(row):
    time = int(row['time'])
    if row['treatment'] == 'De':
        return time
    elif row['treatment'] == 'Re':
        return 24 + time

def format_time_points(df):
    df["time"] = df["time"].str.replace("T", "").astype(int)
    return df
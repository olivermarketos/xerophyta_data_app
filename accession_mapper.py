import requests
from Bio import Entrez
import pandas as pd
import time

# ----------------------------- Configuration -----------------------------

# Set your email here. NCBI requires an email address for Entrez API usage.
Entrez.email = "oliver.marketos@gmail.com"  # Replace with your actual email

# List of accession numbers
accession_numbers = [
    "Q9SZ66",
    "Q9LD44",
    "P47925",
    "Q9ZNS2",
    "NP_683293",
    "Q3E6S8",
    "Q3E6S8",
    "Q3E6S8",
    "Q3E6S8",
    "Q8GWA1",
    "NP_974011"
]

# Output file name
output_file = "accession_mapping.csv"

# ----------------------------- Helper Functions -----------------------------

def fetch_uniprot_data(accessions):
    """
    Fetch data from UniProt for a list of accession numbers.
    """
    url = "https://rest.uniprot.org/uniprotkb/search"
    query = " OR ".join(accessions)  # Create OR query for all accessions
    params = {
        "query": query + " AND organism:Arabidopsis thaliana",
        "fields": "accession,gene_names,organism_name",
        "format": "json",
        "size": len(accessions)
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"UniProt API Error {response.status_code}: {response.text}")
        return {}
    data = response.json()
    results = {}
    for entry in data.get("results", []):
        accession = entry.get("primaryAccession", "")
        gene_names = entry.get("genes", [])
        gene_name = gene_names[0]["geneName"]["value"] if gene_names else "Not Found"
        results[accession] = (gene_name, "Arabidopsis thaliana")
    return results

def fetch_ncbi_data(accessions):
    """
    Fetch data from NCBI for a list of RefSeq accession numbers.
    """
    results = {}
    batch_size = 5
    for i in range(0, len(accessions), batch_size):
        batch = accessions[i:i+batch_size]
        ids = ",".join(batch)
        try:
            handle = Entrez.efetch(db="protein", id=ids, rettype="gb", retmode="text")
            records = handle.read()
            # Basic parsing to extract Gene Name
            for record in records.split("//\n"):
                if "VERSION" in record:
                    acc_line = [line for line in record.split("\n") if line.startswith("VERSION")][0]
                    accession = acc_line.split()[1]
                    gene_name = "Not Found"
                    for line in record.split("\n"):
                        if "/gene=" in line:
                            gene_name = line.split("=")[1].strip('"')
                            break
                    results[accession] = (gene_name, "NCBI RefSeq")
            handle.close()
        except Exception as e:
            print(f"NCBI API Error: {e}")
    return results

# ----------------------------- Main Processing -----------------------------

def main():
    # Separate UniProt and RefSeq accessions
    uniprot_accessions = [acc for acc in accession_numbers if not acc.startswith("NP_")]
    ncbi_accessions = [acc for acc in accession_numbers if acc.startswith("NP_")]

    # Fetch data from UniProt
    print("Fetching data from UniProt...")
    uniprot_data = fetch_uniprot_data(uniprot_accessions)

    # Fetch data from NCBI
    print("Fetching data from NCBI...")
    ncbi_data = fetch_ncbi_data(ncbi_accessions)

    # Compile results
    compiled_data = []
    for acc in accession_numbers:
        if acc in uniprot_data:
            gene_name, source = uniprot_data[acc]
        elif acc in ncbi_data:
            gene_name, source = ncbi_data[acc]
        else:
            gene_name, source = "Not Found", "Not Found"
        compiled_data.append({
            "Accession Number": acc,
            "Source": source,
            "Gene Name": gene_name
        })

    # Save results to CSV
    df = pd.DataFrame(compiled_data)
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    print(df)

if __name__ == "__main__":
    main()

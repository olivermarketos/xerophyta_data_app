import pandas as pd
import numpy as np


def tidy_rna_expression(data):
    data = pd.read_csv(data)

    df = pd.DataFrame(data)
    df.rename(columns={'Unnamed: 0': 'gene_name'}, inplace=True)
    
    # Melt the DataFrame to go from wide to long format
    tidy_df = pd.melt(df, id_vars=['gene_name'], var_name='metadata', value_name='expression')

    # Extract species, treatment, replicate, and time information from the 'metadata' column
    tidy_df[['species', 'treatment', 'replicate', 'time']] = tidy_df['metadata'].str.extract(r'(\w+)_([\w]+)_R(\d+)_T(\d+)')

   
    # make time an integer
    tidy_df['time'] = tidy_df['time'].astype(int)
    tidy_df = tidy_df.sort_values(by=['gene_name'])

    tidy_df= add_log2(tidy_df)

    # add column for total experiment time
    tidy_df['experiment_time'] = tidy_df.apply(calculate_experiment_time, axis=1)
    
     # Reorder the columns for better readability
    tidy_df = tidy_df[['gene_name','time','experiment_time','expression','log2_expression','species', 'treatment', 'replicate', "metadata"]]
    return tidy_df
 
def add_log2(df):
    df["log2_expression"] = np.log2(df['expression']+1)
    return df

def calculate_experiment_time(row):
    time = int(row['time'])
    if row['treatment'] == 'De':
        return time
    elif row['treatment'] == 'Re':
        return 24 + time

def test():
    df = pd.DataFrame(pd.read_csv('data/Xe_seedlings_normalised_counts_tidy.csv'))
    print(df['experiment_time'].unique())


def main():
    df = tidy_rna_expression("data/Xe_seedlings_20_04_DESeq2_normalised_counts_table.csv")
    df.to_csv('data/Xe_seedlings_normalised_counts_tidy.csv', index=False)

 

if __name__ == "__main__":
    main()
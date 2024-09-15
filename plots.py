import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def multi_panel_gene_expression(df):
   
    figures = []
    grouped = df.groupby(['gene_name', 'treatment'])

    # Iterate over the groups and plot each
    for (gene, treatment), group in grouped:
        # Create a new figure for each gene and treatment
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot points for individual replicates
        ax.scatter(group['treatment_time'], group['log2_expression'], label='Replicates', color='blue', alpha=0.6)
        
        # Calculate the mean log2_expression for each treatment_time
        avg_group = group.groupby('treatment_time').agg({'log2_expression': 'mean'}).reset_index()

        # Plot the average line
        ax.plot(avg_group['treatment_time'], avg_group['log2_expression'], label=f"{gene} ({treatment}) Avg", color='black', marker='o')

        # Add labels and title
        ax.set_xlabel('Treatment Time')
        ax.set_ylabel('Log2 Expression')
        ax.set_title(f"Gene: {gene} | {treatment}hydration   ")
        ax.legend()

        figures.append(fig)
    return figures


def single_panel_gene_expression(df):
    figures = []
    
    # Group by treatment (this will group all genes by their treatments)
    grouped = df.groupby('treatment')

    # Iterate over the groups by treatment
    for treatment, group in grouped:
        # Create a new figure for each treatment
        fig, ax = plt.subplots(figsize=(10, 6))

        # Now we need to group by gene_name within the treatment group
        for gene, gene_group in group.groupby('gene_name'):
            # Plot points for individual replicates
            ax.scatter(gene_group['treatment_time'], gene_group['log2_expression'], label=f'{gene} Replicates', alpha=0.6)

            # Calculate the mean log2_expression for each treatment_time
            avg_gene_group = gene_group.groupby('treatment_time').agg({'log2_expression': 'mean'}).reset_index()

            # Plot the average line for this gene
            ax.plot(avg_gene_group['treatment_time'], avg_gene_group['log2_expression'], label=f"{gene} Avg", marker='o')

        # Add labels and title
        ax.set_xlabel('Treatment Time')
        ax.set_ylabel('Log2 Expression')
        ax.set_title(f"Expression of Genes under {treatment}hydration")

        # Add legend
        ax.legend()

        # Append the figure to the list
        figures.append(fig)

    return figures

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def expression_plot(df):
   
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



def expression_plot_old(df):

    bins = [0, 3, 6, 9,12,15,24,25,26,28,32,36,72]

    mean_log2_expression =[]
    binned_stdevs =[] 

    for gene in genes:
        subset = filtered_df[filtered_df['gene_name'] == gene]

        average_log2_expression = subset.groupby('experiment_time')['log2_expression'].mean()
        mean_log2_expression = average_log2_expression.values

        plt.plot(bins,mean_log2_expression , marker='o', label=gene )

    plt.title('Gene Expression Over Time for Selected Genes')
    plt.xlabel('Time')
    plt.ylabel('Log2 expression')
    plt.legend(title='Gene Name')
    plt.grid(True)

    return plt

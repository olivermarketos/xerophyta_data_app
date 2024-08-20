import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def expression_plot(df, genes):

    filtered_df = df[df['gene_name'].isin(genes)]
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

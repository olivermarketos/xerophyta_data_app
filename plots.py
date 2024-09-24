import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def test_multi_panel_gene_expression(df):
    
    figures = []
    grouped = df.groupby(['gene_name', 'treatment'])

    # Iterate over the groups and plot each
    for (gene, treatment), group in grouped:
        # Create a new figure for each gene and treatment
        # fig, ax = plt.subplots(figsize=(8, 6))
        fig, (ax, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')


        # Plot points for individual replicates
        ax.scatter(group['treatment_time'], group['log2_expression'], label='Replicates', color='blue', alpha=0.6)
        ax2.scatter(group['treatment_time'], group['log2_expression'], label='Replicates', color='blue', alpha=0.6)
        
        # Calculate the mean log2_expression for each treatment_time
        avg_group = group.groupby('treatment_time').agg({'log2_expression': 'mean'}).reset_index()

        # Plot the average line
        ax.plot(avg_group['treatment_time'], avg_group['log2_expression'], label=f"{gene} ({treatment}) Avg", color='black', marker='o')
        ax2.plot(avg_group['treatment_time'], avg_group['log2_expression'], label=f"{gene} ({treatment}) Avg", color='black', marker='o')

        ax.set_xlim(0, 30)
        ax2.set_xlim(45, 50)

        ax.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax.yaxis.tick_left()
        ax.tick_params(labelright='off')
        ax2.yaxis.tick_right()
        
        d = .015  # how big to make the diagonal lines in axes coordinates
        # arguments to pass plot, just so we don't keep repeating them
        kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
        ax.plot((1-d, 1+d), (-d, +d), **kwargs)
        #ax.plot((1-d, 1+d), (1-d, 1+d), **kwargs)

        kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
        ax2.plot((-d, +d), (-d, +d), **kwargs)
       
        # Add labels and title
        ax.set_xlabel('Treatment Time')
        ax.set_ylabel('Log2 Expression')
        ax.set_title(f"Gene: {gene} | {treatment}hydration   ")
        ax.legend()

        figures.append(fig)
   
    return figures


   

    
    # hide the spines between ax and ax2
   
    # This looks pretty good, and was fairly painless, but you can get that
    # cut-out diagonal lines look with just a bit more work. The important
    # thing to know here is that in axes coordinates, which are always
    # between 0-1, spine endpoints are at these locations (0, 0), (0, 1),
    # (1, 0), and (1, 1).  Thus, we just need to put the diagonals in the
    # appropriate corners of each of our axes, and so long as we use the
    # right transform and disable clipping.

def multi_panel_gene_expression(df, expression_values):
   
    figures = []
    grouped = df.groupby(['gene_name', 'treatment'])

    # Iterate over the groups and plot each
    for (gene, treatment), group in grouped:
        # Create a new figure for each gene and treatment
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot points for individual replicates
        ax.scatter(group['treatment_time'], group[expression_values], label='Replicates', color='blue', alpha=0.6)
        
        # Calculate the mean log2_expression for each treatment_time
        avg_group = group.groupby('treatment_time').agg({expression_values: 'mean'}).reset_index()

        # Plot the average line
        ax.plot(avg_group['treatment_time'], avg_group[expression_values], label=f"{gene} ({treatment}) Avg", color='black', marker='o')

        ax.set_xticks(group['treatment_time'])
        # Add labels and title
        ax.set_xlabel('Treatment Time')
        ax.set_ylabel(f'{expression_values}')
        ax.set_title(f"Gene: {gene} | {treatment}hydration   ")
        ax.legend()

        figures.append(fig)
    return figures


def single_panel_gene_expression(df, expression_values):
    figures = []
    
    # Group by treatment (this will group all genes by their treatments)
    grouped = df.groupby('treatment')

    fig_width, fig_height = 10, 6

    # Iterate over the groups by treatment
    for treatment, group in grouped:
        # Create a new figure for each treatment
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        unique_gene_labels = [] 
        for gene, gene_group in group.groupby('gene_name'):
            # Plot points for individual replicates
            ax.scatter(gene_group['treatment_time'], gene_group[expression_values], label=f'{gene}', alpha=0.6)

            # Calculate the mean log2_expression for each treatment_time
            avg_gene_group = gene_group.groupby('treatment_time').agg({expression_values: 'mean'}).reset_index()

            # Plot the average line for this gene
            ax.plot(avg_gene_group['treatment_time'], avg_gene_group[expression_values], marker='o')

            if gene not in unique_gene_labels:
                unique_gene_labels.append(gene)
       
        ax.set_xticks(group['treatment_time'])

        # Add labels and title
        ax.set_xlabel('Treatment Time',)
        ax.set_ylabel(f'{expression_values}')
        ax.set_title(f"Expression of Genes under {treatment}hydration")

        ax.legend()
        if treatment == "Re":
            # Add legend
            ax.get_yaxis().set_visible(False)

        # Append the figure to the list 
        figures.append(fig)

    return figures

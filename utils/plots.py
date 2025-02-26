import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.size'] = 14  # increases the base font size
mpl.rcParams['axes.labelsize'] = 16  # label font size
mpl.rcParams['axes.titlesize'] = 18  # title font size
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14



def test_multi_panel_gene_expression(df):
    
    figures = []
    grouped = df.groupby(['gene_name', 'treatment'])

    # Iterate over the groups and plot each
    for (gene, treatment), group in grouped:
        # Create a new figure for each gene and treatment
        # fig, ax = plt.subplots(figsize=(8, 6))
        fig, (ax, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')


        # Plot points for individual replicates
        ax.scatter(group['time'], group['log2_expression'], label='Replicates', color='blue', alpha=0.6)
        ax2.scatter(group['time'], group['log2_expression'], label='Replicates', color='blue', alpha=0.6)
        
        # Calculate the mean log2_expression for each time
        avg_group = group.groupby('time').agg({'log2_expression': 'mean'}).reset_index()

        # Plot the average line
        ax.plot(avg_group['time'], avg_group['log2_expression'], label=f"{gene} ({treatment}) Avg", color='black', marker='o')
        ax2.plot(avg_group['time'], avg_group['log2_expression'], label=f"{gene} ({treatment}) Avg", color='black', marker='o')

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


   


def multi_panel_gene_expression(df, expression_values):
   
    figures = []
    grouped = df.groupby(['gene_name', 'treatment'])

    # Iterate over the groups and plot each
    for (gene, treatment), group in grouped:
        # Create a new figure for each gene and treatment
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot points for individual replicates
        ax.scatter(group['time'], group[expression_values], label='Replicates', color='blue', alpha=0.6)
        
        # Calculate the mean log2_expression for each time
        avg_group = group.groupby('time').agg({expression_values: 'mean'}).reset_index()

        # Plot the average line
        ax.plot(avg_group['time'], avg_group[expression_values], label=f"{gene} ({treatment}) Avg", color='black', marker='o')

        ax.set_xticks(group['time'])
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
            ax.scatter(gene_group['time'], gene_group[expression_values], label=f'{gene}', alpha=0.6)

            # Calculate the mean log2_expression for each time
            avg_gene_group = gene_group.groupby('time').agg({expression_values: 'mean'}).reset_index()

            # Plot the average line for this gene
            ax.plot(avg_gene_group['time'], avg_gene_group[expression_values], marker='o')

            if gene not in unique_gene_labels:
                unique_gene_labels.append(gene)
       
        ax.set_xticks(group['time'])

        # Add labels and title
        ax.set_xlabel('Treatment Time',)
        ax.set_ylabel(f'{expression_values.split("_")[0]} expression')
        ax.set_title(f"Expression of Genes under {treatment}hydration")

        # ax.legend()
       

        if treatment == "Re":
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            plt.tight_layout()
            # ax.get_yaxis().set_visible(False)

        # Append the figure to the list 
        figures.append(fig)

    return figures
def dual_panel_gene_expression(df, expression_values):
    grouped = df.groupby('treatment')
    treatments = sorted(grouped.groups.keys())
    
    fig_width, fig_height = 10, 6
    fig, axs = plt.subplots(1, 2, figsize=(2 * fig_width, fig_height), sharey=True)
    
    legend_handles = {}  # store each gene's scatter handle and color for consistency
    
    for ax, treatment in zip(axs, treatments):
        group = grouped.get_group(treatment)
        times = sorted(group['time'].unique())
        ax.set_xticks(times)
        
        for gene, gene_group in group.groupby('gene_name'):
            if gene not in legend_handles:
                sc = ax.scatter(gene_group['time'], gene_group[expression_values],
                                label=gene, alpha=0.6)
                color = sc.get_facecolors()[0]
                legend_handles[gene] = (sc, color)
            else:
                color = legend_handles[gene][1]
                ax.scatter(gene_group['time'], gene_group[expression_values],
                           color=color, alpha=0.6)
            
            avg_gene_group = gene_group.groupby('time').agg({expression_values: 'mean'}).reset_index()
            ax.plot(avg_gene_group['time'], avg_gene_group[expression_values],
                    marker='o', color=color)
        
        ax.set_xlabel('Treatment Time')
        ax.set_title(f"Expression of Genes under {treatment}hydration")
        if ax == axs[0]:
            ax.set_ylabel(f'{expression_values.split("_")[0]} expression')
    
    # Create a single legend outside the plots on the right side.
    handles = [handle for handle, _ in legend_handles.values()]
    labels = list(legend_handles.keys())
    fig.legend(handles, labels,
               loc='right',
               title="Genes", fontsize='small')
    
    # Adjust subplots to allocate space for the legend on the right.
    fig.subplots_adjust(right=0.8)
    
    return fig

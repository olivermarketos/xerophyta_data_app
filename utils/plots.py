import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.size'] = 14  # increases the base font size
mpl.rcParams['axes.labelsize'] = 16  # label font size
mpl.rcParams['axes.titlesize'] = 18  # title font size
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14



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

def individual_gene_expression(df, expression_values):
    """
    Creates a figure with one row per gene. For each gene, the left panel shows the dehydration data
    and the right panel shows the rehydration data. Each panel plots individual sample points along with 
    the average line across time.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing columns 'gene_name', 'treatment', 'time', and the 
                           expression values (e.g., 'log2_expression').
        expression_values (str): The name of the expression column in df.
        
    Returns:
        fig (matplotlib.figure.Figure): The combined figure.
    """
    # Get unique genes
    genes = df['gene_name'].unique()
    
    # Define a fixed treatment order and mapping to full names.
    # Adjust these if your treatment labels are different.
    treatment_order = ['De', 'Re']
    treatment_mapping = {'De': 'Dehydration', 'Re': 'Rehydration'}

    # Set up figure dimensions: two columns for the two treatments and one row per gene.
    fig_width, fig_height = 5, 4
    n_rows = len(genes)
    fig, axs = plt.subplots(n_rows, 2, figsize=(2 * fig_width, n_rows * fig_height), 
                              sharex=True, sharey=True)
    
    # If there's only one gene, force axs to be 2D.
    if n_rows == 1:
        axs = np.array([axs])
    
    # Loop over genes (rows)
    for i, gene in enumerate(genes):
        gene_data = df[df['gene_name'] == gene]
        
        # Loop over treatments (columns)
        for j, treatment in enumerate(treatment_order):
            ax = axs[i, j]
            treatment_data = gene_data[gene_data['treatment'] == treatment]
            
            if treatment_data.empty:
                # If no data for this treatment, indicate it.
                ax.set_title(f"{gene} - {treatment_mapping[treatment]} (No Data)")
            else:
                # Plot individual sample points
                ax.scatter(treatment_data['time'], treatment_data[expression_values], alpha=0.6)
                
                # Compute and plot the average expression per time point
                avg_df = treatment_data.groupby('time', as_index=False).agg({expression_values: 'mean'})
                ax.plot(avg_df['time'], avg_df[expression_values], marker='o')
                
                ax.set_title(f"{gene} - {treatment_mapping[treatment]}")
                # Set x-ticks based on the unique time points
                ax.set_xticks(sorted(treatment_data['time'].unique()))
            
            ax.set_xlabel('Treatment Time')
            # Only add the y-axis label on the left column for clarity
            if j == 0:
                ax.set_ylabel(f'{expression_values.split("_")[0]} expression')
    
    plt.tight_layout()
    return fig
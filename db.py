import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
import models as models
import pandas as pd
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func


class DB():

    DATABASE_NAME = "xerophyta_db.sqlite"

    def __init__(self) -> None:
        
        self.engine = sq.create_engine(f"sqlite:///{self.DATABASE_NAME}", echo = False)
        self.conn = self.engine.connect()

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_or_update(self, model, values, pk):
        """
        Generic method to create or update any record in any model and return an instance of that record.

        Also works for batch insertions or updates, in which case the last record of the batch job is returned.

        Parameters:
            model: the model (or table) in which to perform the Create or Update task
            values: a list of dictionaries specifying the values the new record should contain
            pk: the primary key of this table, as a string
        """


        for value in values:

            instance = self.session.query(model).get(value[pk])
            
            if instance is not None:

                instance = self.session.merge(model(**value))
                self.session.commit()

            else:
                instance = model(**value) 
                self.session.add(instance)
                self.session.commit()


        return instance

    def batch_create_or_update(self, model, values, pk):
         
        """ 
        Generic method to create or update any record in any model and return an instance of that record.

            Also works for batch insertions or updates, in which case the last record of the batch job is returned.

            Parameters:
                model: the model (or table) in which to perform the Create or Update task
                values: a list of dictionaries specifying the values the new record should contain
                pk: the primary key of this table, as a string
        """
        batch_size = 1000
        instances = []

        for i, value in enumerate(values):

            instance = self.session.query(model).get(value[pk])
            
            if instance is not None:
                instance = self.session.merge(model(**value))

            else:
                instance = model(**value) 
                self.session.add(instance)

            instances.append(instance)

            # process the records in batches before committing
            if(i+1)% batch_size == 0:
                self.session.commit()
                instances = []

        if instances:
            self.session.commit()
        return instances[-1] if instances else None

    def add_gene_locus(self, model, values):
        """ 
        Update gene_location in the database by mapping it to Hit_acc.

        Parameters:
            model: the model (or table) to update
            df: a pandas DataFrame containing 'Hit_acc' and 'gene_location'
        """

        for i, value in enumerate(values):
            # Find the instance by matching Hit_acc
            instances = self.session.query(model).filter_by(Hit_ACC=value['Hit_ACC']).all()
            
            for instance in instances:
                if instance is not None:
                    instance.At_locus_id = value['At_locus_id']
                    instance.At_gene_name = value['At_gene_name']


        if instances:
            self.session.commit()


    # pass dictionary with 
    def add_at_homologues(self, acc_num, at_locus, common_name_list):
        xe_gene = self.session.query(models.Gene_info).filter(models.Gene_info.Hit_ACC== acc_num).all()
    
        # Step 3: Create or retrieve Arabidopsis homologue data
        # First, check if the homologue already exists
        homologue = self.session.query(models.Arabidopsis_Homologue).filter(models.Arabidopsis_Homologue.accession_number==acc_num).first()

        # If the homologue doesn't exist, create it
        if homologue is None:
            homologue = models.Arabidopsis_Homologue(
                accession_number=acc_num,
                at_locus= at_locus # Example locus
            )
            self.session.add(homologue)

        # Step 4: Add common names
        # Assuming we have multiple common names for this accession number

        for name in common_name_list:
        #     # Check if the common name exists for this homologue
            existing_common_name = self.session.query(models.At_Common_Names).filter_by(name=name, arabidopsis_id=homologue.arabidopsis_id).first()

            if existing_common_name is None:
                common_name = models.At_Common_Names(name=name, homologue=homologue)
                self.session.add(common_name)

        #  Step 5: Associate the XeGene with the Arabidopsis homologue (many-to-many relationship)
        for gene in xe_gene:

            if homologue not in gene.homologues:
                gene.homologues.append(homologue)

        # Step 6: Commit the transaction
        self.session.commit()

    def get_gene_expression_data(self, gene_list):
        """
        Query the database to retrieve gene expression data for a list of genes.

        Parameters:
            gene_list (list): A list of gene names to query.

        Returns:
            pandas.DataFrame: A DataFrame containing the gene expression data.
        """
        # Ensure gene_names is a list or tuple
        if isinstance(gene_list, str):
            gene_list = [gene_list]
        
        query = self.session.query(models.Gene_expressions).filter(models.Gene_expressions.gene_name.in_(gene_list)).all()
        
        data = [record.__dict__ for record in query]

        # Remove SQLAlchemy internal keys (_sa_instance_state)
        for row in data:
            row.pop('_sa_instance_state', None)

        df = pd.DataFrame(data)
        return df

    def get_gene_from_arab_homolog(self, At_list):
        
        result =(self.session.query(models.Gene_info.gene_name, models.Arabidopsis_Homologue.at_locus, models.At_Common_Names.name)
            .join(models.Gene_info.homologues)  # Join Gene_info with Arabidopsis_Homologue using the relationship
            .join(models.Arabidopsis_Homologue.common_names)  # Join Arabidopsis_Homologue with At_Common_Names
            .filter(
                or_(
                    func.lower(models.Arabidopsis_Homologue.at_locus).in_([x.lower() for x in At_list]),  # Case-insensitive for homologues
                    func.lower(models.At_Common_Names.name).in_([x.lower() for x in At_list])  # Case-insensitive for common names
                )
            )
            .all()
        )
        return result 
    
    def match_homologue_to_Xe_gene(self, At_list):
        # Create a DataFrame with the queries
        query_df = pd.DataFrame()
        query_df["Query"] = At_list

        # Get the hits from the database
        hits = self.get_gene_from_arab_homolog(At_list)

        # Prepare the results DataFrame
        results = []
        for hit in hits:
            xele_gene, at_gene, common_name = hit
            # Here we assume that 'at_gene' or 'common_name' is one of the original queries
            if at_gene.lower() in [x.lower() for x in At_list]:
                query = at_gene
            else:
                query = common_name

            results.append({
                'Query': query,  # Add the matching query here for alignment
                'Xele_Gene': xele_gene,
                'At_Gene': at_gene,
                'Common_name': common_name
            })

        # Create a DataFrame from the results
        results_df = pd.DataFrame(results)

        # Merge the query DataFrame with the results DataFrame
        final_df = pd.merge(query_df, results_df, on='Query', how='left')

        return final_df

    def get_gene_from_arab_name(self, At_list):
        
        query = self.session.query(models.Gene_info.gene_name, models.Gene_info.At_gene_name).filter(
            *[models.Gene_info.At_gene_name.like(f'%{gene}%') for gene in At_list]
            ).all()
        return query
    
    def get_uniprot_id(self):
        query = self.session.query(models.Gene_info.Hit_ACC).all()
        return query

    def genes_no_info(self):
        results = self.session.query(models.Gene_info.gene_name).filter(models.Gene_info.sequence_description == None).all()
        return results

    def genes_from_seqdata(self):
        results = self.session.query(models.Gene_expressions.gene_name).distinct().all()
        return results
    
    def get_gene_names(self):
        results = self.session.query(models.Gene_info.gene_name).all()
        return results
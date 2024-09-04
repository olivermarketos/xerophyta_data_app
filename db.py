import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
import models


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




    def get_expression_by_gene_name(self, gene_names):
    # Ensure gene_names is a list or tuple
        if isinstance(gene_names, str):
            gene_names = [gene_names]
        
        expressions = self.session.query(models.Gene_expressions).filter(models.Gene_expressions.gene_name.in_(gene_names)).all()
        return expressions



import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.db import DB

@pytest.fixture
def temp_db():
    """Create a temporary in-memory SQLite database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    engine = create_engine(f'sqlite:///{temp_file.name}')
    Base.metadata.create_all(engine)
    
    yield temp_file.name
    
    os.unlink(temp_file.name)

@pytest.fixture
def db_instance(temp_db, monkeypatch):
    """Create a DB instance with a temporary database."""
    monkeypatch.setattr(DB, 'DATABASE_NAME', temp_db)
    return DB()

@pytest.fixture
def sample_gene_data():
    """Sample gene data for testing."""
    return {
        'gene_names': ['Xele.ptg000001l.104', 'Xele.ptg000002l.205'],
        'species_name': 'X. elegans',
        'go_terms': ['GO:0003677', 'GO:0006355'],
        'arabidopsis_loci': ['AT1G01010', 'AT1G01020']
    }
# Xerophyta Data Explorer

A web application for exploring transcriptomic data from *Xerophyta* resurrection plants. This tool enables researchers to query gene annotations, visualise time-series expression profiles, and explore gene regulatory networks.

**Live application:** https://xerophyta-data-explorer.streamlit.app

## Features

### Gene Info
Query the database to retrieve comprehensive gene annotation information:
- BLAST annotations (e-value, bit score, similarity, alignment length)
- Gene Ontology (GO) terms
- Enzyme codes (EC numbers)
- InterPro protein domains
- *Arabidopsis thaliana* ortholog mappings

Search by Xerophyta gene ID, Arabidopsis ortholog (locus ID or common name), GO term, or enzyme code. Results can be downloaded as CSV or FASTA files.

### Gene Expression
Visualise time-series gene expression profiles during dehydration and rehydration treatments:
- Plot log2 or normalised expression values
- Filter by differential expression status (all, up-regulated, down-regulated)
- Display genes on a single combined plot or separate panels
- Download plots as PNG or ZIP archives
- Export underlying expression data as CSV

### Gene Regulatory Network
Explore inferred transcriptional regulatory interactions:
- Filter by regulator gene, target gene, or cluster
- Filter by direction of regulation (activation, repression, unknown)
- Download filtered results as CSV
- Currently available for *X. elegans* only

## Species

The database contains transcriptomic data for three *Xerophyta* species:
- *Xerophyta elegans*
- *Xerophyta schlechteri*
- *Xerophyta humilis*

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/olivermarketos/xerophyta_data_app.git
cd xerophyta_data_app
```

2. Create a virtual environment and install dependencies:

**Using uv (recommended):**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Using pip:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Database

The SQLite database file (`database/data/all_xerophyta_species_db.sqlite`) is required to run the application. Due to its size (~500 MB), it is not included in the repository.

To obtain the database:
- Contact the authors (see below)
- Or download from [Zenodo DOI link]

Place the database file in `database/data/`.

## Running Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Project Structure

```
xerophyta_data_app/
├── app.py                 # Main Streamlit entry point
├── server/
│   ├── home.py            # Home page
│   ├── expression_page.py # Gene expression visualisation
│   ├── gene_query_page.py # Gene annotation queries
│   ├── grn_explorer.py    # Gene regulatory network explorer
│   └── images/            # Species images
├── database/
│   ├── db.py              # Database query functions
│   ├── models.py          # SQLAlchemy ORM models
│   ├── db_manager.py      # Database management utilities
│   └── data/              # SQLite database files
├── utils/
│   ├── constants.py       # Application constants
│   ├── helper_functions.py# Utility functions
│   └── plots.py           # Plotting functions
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Project configuration
```

## Contact

For bug reports, feature requests, or questions:
- Email: olivermarketos@gmail.com
- GitHub Issues: https://github.com/olivermarketos/xerophyta_data_app/issues

## License

This project is licensed under the MIT License - see below for details.

```
MIT License

Copyright (c) 2025 Oliver Marketos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

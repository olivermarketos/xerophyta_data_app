# Xerophyta Data Explorer

A web application for exploring transcriptomic data from *Xerophyta* resurrection plants. This tool enables researchers to query gene annotations, visualise time-series expression profiles during dehydration and rehydration, and explore gene regulatory networks across three *Xerophyta* species.

**Live application:** https://xerophyta-data-explorer.streamlit.app

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start (experienced users)](#quick-start)
- [Step-by-step installation (beginners)](#step-by-step-installation)
  - [Step 1 — Install Python](#step-1--install-python)
  - [Step 2 — Download the code](#step-2--download-the-code)
  - [Step 3 — Install dependencies](#step-3--install-dependencies)
  - [Step 4 — Download the database](#step-4--download-the-database)
  - [Step 5 — Run the app](#step-5--run-the-app)
- [Using the app](#using-the-app)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Citation](#citation)
- [Contact](#contact)
- [License](#license)

---

## Overview

*Xerophyta* is a genus of resurrection plants native to sub-Saharan Africa, Madagascar, and the Arabian Peninsula. These plants are remarkable for their ability to survive complete desiccation and recover upon rehydration. This application provides a browser-based interface to the transcriptomic datasets generated from three *Xerophyta* species:

| Species | Notes |
|---|---|
| *Xerophyta elegans* | Homoiochlorophyllous; retains chlorophyll during desiccation. Seedling time-course covers 7 dehydration and 7 rehydration time points. |
| *Xerophyta schlechteri* | Poikilochlorophyllous; degrades chlorophyll during desiccation. |
| *Xerophyta humilis* | Poikilochlorophyllous. |

The application is intended as a companion resource to the following manuscript:

> Kabwe E.N.K., Edwards M.P., Lyall R., Ngcala M., Schlebusch S.A., Marketos O.P., VanBuren R., Nikoloski Z., Ingle R.A. and Illing N. *Transcriptional regulation of the response to water availability in the resurrection plant* Xerophyta elegans. *(Submitted manuscript.)*

---

## Features

### Gene Expression
Visualise how individual genes change in expression over the course of dehydration and rehydration:
- Plot log2 or normalised expression values across time points
- Filter by differential expression status: all genes, up-regulated, or down-regulated
- Display multiple genes on a single combined plot or on separate panels
- Download plots as PNG files or as a ZIP archive
- Export the underlying expression values as a CSV file

### Gene Info
Query comprehensive annotation data for any gene in the database:
- BLAST annotations (e-value, bit score, percent similarity, alignment length)
- Gene Ontology (GO) terms
- Enzyme Commission (EC) numbers
- InterPro protein domain assignments
- *Arabidopsis thaliana* ortholog mappings

Search by *Xerophyta* gene ID, *Arabidopsis* locus ID or common name, GO term, or enzyme code. Results can be downloaded as a CSV table or as a FASTA sequence file.

### Gene Regulatory Network (GRN)
Explore inferred transcriptional regulatory interactions between transcription factors and their target genes:
- Filter by regulator gene, target gene, or co-expression cluster
- Filter by direction of regulation (activation, repression, or unknown)
- Download filtered results as a CSV file
- Currently available for *X. elegans* only

---

## Quick Start

If you are familiar with Python and the command line, these four commands are all you need after downloading the database file (see [Step 4](#step-4--download-the-database)):

```bash
git clone https://github.com/olivermarketos/xerophyta_data_app.git
cd xerophyta_data_app
pip install -r requirements.txt
streamlit run app.py
```

---

## Step-by-step installation

This section is written for readers who may not have prior experience with Python or the command line. Each step is explained in plain terms. You do not need to understand how the code works — you just need to follow these steps to get the app running on your own computer.

### What you will need

- A computer running **macOS**, **Windows**, or **Linux**
- An internet connection (for the initial setup)
- Approximately **1.5 GB** of free disk space (for Python, dependencies, and the database)

---

### Step 1 — Install Python

Python is a free programming language. The app is written in Python and requires it to run. You only need to install Python once.

**Check if Python is already installed**

Open a terminal (see the note below if you are unsure how to do this) and type:

```bash
python --version
```

or

```bash
python3 --version
```

If you see a version number of **3.11 or higher** (e.g. `Python 3.11.4`), Python is already installed and you can skip to Step 2.

> **How to open a terminal**
> - **macOS**: Press `Command + Space`, type `Terminal`, and press Enter.
> - **Windows**: Press `Windows + R`, type `cmd`, and press Enter. Alternatively, search for "Command Prompt" or "PowerShell" in the Start menu.
> - **Linux**: Press `Ctrl + Alt + T`, or search for "Terminal" in your applications.

**Install Python**

If Python is not installed, download the installer from the official Python website:

- **macOS / Windows / Linux**: https://www.python.org/downloads/

Download the latest **Python 3.11.x** or **3.12.x** installer for your operating system and follow the on-screen instructions.

> **Windows users**: During installation, tick the box that says **"Add Python to PATH"** before clicking Install. This is important.

---

### Step 2 — Download the code

You have two options: download a ZIP file, or use Git.

**Option A — Download as ZIP (recommended for beginners)**

1. Go to the GitHub repository page: https://github.com/olivermarketos/xerophyta_data_app
2. Click the green **Code** button near the top right of the page.
3. Select **Download ZIP**.
4. Once downloaded, unzip (extract) the folder to a location you can find easily, such as your Desktop or Documents folder.

**Option B — Use Git (for users familiar with Git)**

If you have Git installed, you can clone the repository:

```bash
git clone https://github.com/olivermarketos/xerophyta_data_app.git
```

---

### Step 3 — Install dependencies

The app relies on several Python libraries (tools that extend what Python can do). These need to be installed once.

**Open a terminal and navigate to the project folder**

In your terminal, change directory to wherever you saved the project folder. For example, if you extracted the ZIP to your Desktop:

- **macOS / Linux**:
  ```bash
  cd ~/Desktop/xerophyta_data_app
  ```

- **Windows**:
  ```
  cd C:\Users\YourName\Desktop\xerophyta_data_app
  ```

Replace `YourName` with your actual Windows username.

> **Tip**: You can drag the project folder from Finder or File Explorer into the terminal window instead of typing the path. On Mac, type `cd ` (with a space) first, then drag the folder in.

**Create a virtual environment (recommended)**

A virtual environment is an isolated workspace that keeps the app's dependencies separate from other Python software on your computer. It is not strictly required, but it is good practice.

- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows**:
  ```
  python -m venv .venv
  .venv\Scripts\activate
  ```

You will see `(.venv)` appear at the start of your terminal prompt, indicating the environment is active.

**Install the required libraries**

With your virtual environment active (or without one if you skipped that step), run:

```bash
pip install -r requirements.txt
```

This will download and install all necessary packages. It may take a few minutes depending on your internet speed. You should see a series of progress messages ending with `Successfully installed ...`.

---

### Step 4 — Download the database

The app's data is stored in a single SQLite database file (~500 MB). Because of its size, it is not bundled with the code on GitHub and must be downloaded separately.

**Download the database file:**

The database is archived at the following location:

> **[Zenodo DOI — TODO]**

Download the file named `all_xerophyta_species_db.sqlite` and place it in the following folder inside your project directory:

```
xerophyta_data_app/
└── database/
    └── data/
        └── all_xerophyta_species_db.sqlite   ← place the file here
```

The `database/data/` folder already exists in the project. You just need to copy the downloaded `.sqlite` file into it.

> If you cannot find the database file at the link above, contact the authors at olivermarketos@gmail.com.

---

### Step 5 — Run the app

Make sure you are in the project folder in your terminal (the same terminal where you installed dependencies in Step 3). If you created a virtual environment, make sure it is still active (you will see `(.venv)` in your prompt).

Start the app by running:

```bash
streamlit run app.py
```

After a few seconds you should see a message like:

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Your default web browser should open automatically and display the app. If it does not, open your browser and go to: **http://localhost:8501**

> **To stop the app**, return to the terminal and press `Ctrl + C`.

> **To run the app again** in a later session, open a terminal, navigate to the project folder, activate the virtual environment if you created one, and run `streamlit run app.py` again.

---

## Using the app

The app has four pages, accessible from the sidebar on the left:

### Home
An introduction to the project with background information on each *Xerophyta* species and brief descriptions of each page.

### Expression Data
1. Select a species from the dropdown at the top.
2. Enter one or more gene IDs in the text box (one per line, or separated by commas).
3. Choose whether to plot log2 or normalised expression values.
4. Use the filter options to restrict to up-regulated or down-regulated genes if desired.
5. Click **Plot** to generate the expression profiles.
6. Use the download buttons beneath each plot to save the image or the data.

### Gene Info
1. Select a species.
2. Choose a search type from the dropdown: gene ID, *Arabidopsis* locus ID, common name, GO term, or enzyme code.
3. Enter your search term and press Enter or click **Search**.
4. Browse the result tables, which are organised by annotation type.
5. Use the download buttons to export results as CSV or FASTA.

### Gene Regulatory Network
1. Use the filter inputs to search by regulator, target gene, cluster, or direction of regulation.
2. The network table will update automatically.
3. Click **Download CSV** to export the filtered interactions.

---

## Troubleshooting

**"Command not found: python" or "Command not found: python3"**
Python is not installed or not on your PATH. Return to [Step 1](#step-1--install-python). On Windows, re-run the Python installer and ensure "Add Python to PATH" is checked.

**"No module named streamlit" or similar import errors**
The dependencies are not installed in the currently active Python environment. Make sure your virtual environment is activated (you should see `(.venv)` in the prompt) and re-run `pip install -r requirements.txt`.

**The app opens but shows a database error or no data appears**
The database file is missing or in the wrong location. Check that `all_xerophyta_species_db.sqlite` is inside `database/data/`. The full path from the project root should be `database/data/all_xerophyta_species_db.sqlite`.

**The browser does not open automatically**
Open your browser manually and navigate to http://localhost:8501.

**Port 8501 is already in use**
Another instance of the app may be running. Stop it with `Ctrl + C` in the terminal, or run the app on a different port:
```bash
streamlit run app.py --server.port 8502
```
Then open http://localhost:8502 in your browser.

**Plots are slow to load or the app is unresponsive**
The expression data page limits display to a maximum number of genes by default. If querying a large gene set, try a smaller subset first.

**Windows-specific: `.venv\Scripts\activate` returns an error about execution policy**
Run this command in PowerShell and try again:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Still stuck?**
Open an issue on GitHub (https://github.com/olivermarketos/xerophyta_data_app/issues) or email olivermarketos@gmail.com describing the error message and what operating system you are using.

---

## Project structure

```
xerophyta_data_app/
├── app.py                       # Main entry point (run this to start the app)
├── requirements.txt             # Python package dependencies
├── pyproject.toml               # Project metadata and build configuration
├── server/
│   ├── home.py                  # Home page
│   ├── expression_page.py       # Expression data visualisation
│   ├── gene_query_page.py       # Gene annotation queries
│   ├── grn_explorer.py          # Gene regulatory network explorer
│   └── images/                  # Species and lab images
├── database/
│   ├── models.py                # Database table definitions (SQLAlchemy ORM)
│   ├── db.py                    # Query functions
│   ├── db_manager.py            # Database management utilities
│   ├── migrations/              # Alembic schema migration history
│   └── data/
│       └── all_xerophyta_species_db.sqlite   # ← database file goes here
├── utils/
│   ├── constants.py             # Shared constants
│   ├── helper_functions.py      # Utility functions
│   ├── plots.py                 # Plotting functions
│   └── data_tidier.py           # Data processing utilities
└── tests/                       # Pytest test suite
```

---

## Citation

If you use this application or the underlying datasets in your research, please cite:

> Kabwe E.N.K., Edwards M.P., Lyall R., Ngcala M., Schlebusch S.A., Marketos O.P., VanBuren R., Nikoloski Z., Ingle R.A. and Illing N. *Transcriptional regulation of the response to water availability in the resurrection plant* Xerophyta elegans. *(Submitted manuscript.)*

---

## Contact

- **Bug reports and feature requests**: https://github.com/olivermarketos/xerophyta_data_app/issues
- **Email**: olivermarketos@gmail.com

---

## License

This project is released under the MIT License.

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

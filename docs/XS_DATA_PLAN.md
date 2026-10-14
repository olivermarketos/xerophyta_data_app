# Plan: Add X. schlechteri seedling data to the Xerophyta Data Explorer

## Context
New X. schlechteri seedling data is waiting in `all_data/to_add/X schlechteri/`:
- normalised counts (24,241 genes × 77 samples)
- DEG table (13,589 genes)
- GRN (965,707 interactions)
- GRN figure `Railplopt_cluster_network_Xs.tiff`

Loader cells are already written and tested on a DB copy (`notebooks/workflow_notes.ipynb`, section "14 October 2026"). None of it has been run on the real DB yet.

Open questions have been sent to the biologist (`Xs_data_questions.md`/`.pdf`, `Xs_sample_sheet_for_review.csv`):
- whether the two sample batches are the same plants sequenced again
- the `ReT02_R3` technical duplicate
- two possibly mislabelled samples
- 40 revised gene models with no sequence or annotation

The app is effectively X. elegans-only:
- the expression page forces the species back to X. elegans
- the GRN page has no species filter and a hard-coded figure
- the home page only has an X. elegans tab

Goal: load the data safely and make every page species-aware, so X. schlechteri is selectable and shown correctly.

Scope (decided):
- **This plan:** the X. schlechteri work plus the minimum schema fixes from `docs/HANDOVER_PLAN.md` Phase 1 that the new data makes necessary.
- **Left to the handover plan:** the loader package, sample-sheet system and repo cleanup.
- **UX:** a **per-page species selector**, each listing only species that have data for that page.

---

## Step 0: Decisions from the biologist
Each answer feeds a specific step below. Answers received 14 Oct 2026.

| Question | Answer | Affects | Action |
|---|---|---|---|
| Batch A vs B: same plants? Combine, keep both, or drop one? | **Answered.** Two independent sets of experiments, sequenced at different times. Their replicate numbers are independent. Treat as additional biological repeats and combine them, as was done in all their analyses. | Step 2 | No change: keep both. Batch B replicates keep the `b` suffix (`R3b`) so they don't collide with batch A replicate names. |
| `ReT02_R3_…732/…733` technical duplicates? | **Answered.** Biological replicates, not technical: the same time point and rehydration run. BGI appended its sequencing IDs to tell them apart. | Step 2 | No change: keep both as separate replicates (`R3_8522311005732`, `R3_8522311005733`). |
| `Xs_Des_R3_T15`, `Xs_Reh_R5_T04` mislabelled? | **Answered.** Already flagged by them on PCA. If mislabelled, it happened before sequencing and can't be traced. Kept in, because there are enough replicates that they don't cause a significant issue. | Step 2 | No change: keep as labelled. |
| Sequences for the revised `_NEW` genes | **Received** `all_data/to_add/Xsch_47_updated_seqs.fasta`, 47 records: the 40 genes missing from the DB, 6 more split parts not in the counts table, and a revised sequence for `Xsch.v2.MJHO01000004.1.247`. See Step 3. | Step 3 | Load. |
| Annotation (blast2go) for the new genes; remove the 22 old genes? | **Open.** No annotation file came with the FASTA, and removal of the old models wasn't confirmed. | Step 3 | Ask. |
| X. schlechteri Arabidopsis TAIR mapping (Xs has 0 homologue rows) | **Open.** | Step 3b | none |
| Home-page text for X. schlechteri (description, dataset, reference) and the GRN figure caption | **Open.** | Step 5 | placeholder |

## Step 1: Minimum schema fixes (one Alembic revision, before loading)
New revision in `database/migrations/alembic/versions/`, using `op.batch_alter_table` (SQLite). Current head is `aded5eaefd2d`.
- **Indexes** (`gene_expressions` has none; the GRN target lookups and expression queries scan the whole table, and both tables are about to grow 1.5–3×):
  - `gene_expressions(gene_id)`, `(experiment_id)`
  - `regulatory_interactions(target_gene_id)`, `(regulatory_cluster)`
  - `genes(species_id)`
- **Unique constraint** `gene_expressions(experiment_id, gene_id, treatment, time, replicate)`. HANDOVER_PLAN verified it applies cleanly to the current data. Mirror it in `database/models.py` (`Gene_expressions.__table_args__`) and add `index=True` to the indexed columns.
- **Data step:** set `experiments.species_id = 1` for `xe_seedlings_time_course` (currently NULL). The X. schlechteri experiment is linked by the notebook (`link_experiment_to_species`).
- **Upsert-key bug:** fix `database/db_manager.py:138` (`add_rna_seq_data` lookup key) to include `experiment_id`, in the same commit. This prevents a future load overwriting another experiment's rows.
- `delete_genes_by_names` (`database/db.py:815`): remove `cleanup_orphans` from the docstring, so the Step 3 call matches the real signature.

## Step 2: Load the X. schlechteri data (real DB)
Use the existing notebook section in `notebooks/workflow_notes.ipynb`. It backs up the DB, tidies the data, bulk-inserts, refuses to run twice, and prints a summary.

The biologist's answers (Step 0) confirm the notebook's current sample handling, so the tidy and load cells need no changes:
- Both batches are combined as biological repeats; batch B keeps the `b` replicate suffix.
- Both `ReT02_R3_*` samples are kept as separate biological replicates.
- The two PCA outliers are kept as labelled.
- `log2_expression` = `log2(normalised + 1)` (`USE_LOGCPM_FOR_LOG2 = False`).

Update the notebook's "Assumptions / questions" markdown to record these answers.

After loading, compare row counts before and after. X. elegans must stay at 984,942 expression rows.

## Step 3: Revised gene models
Sequences received: `all_data/to_add/Xsch_47_updated_seqs.fasta` (47 records, all valid nucleotide sequences, no duplicate IDs). What the 47 records are:
- **40** `_NEW` genes that are in the counts table but missing from the DB. All 40 are in the FASTA.
- **6** more split parts that are **not** in the counts table, DEG or GRN files: `…01000001.1.274_A_NEW`, `…01000010.1.471_B_NEW`, `…01000043.1.103_A_NEW`, `…01000043.1.103_C_NEW`, `…01000054.1.132_A_NEW`, `…01000060.1.126_B_NEW`. They'll be added as genes with no expression data, presumably filtered out upstream (e.g. low counts).
- **1** revised sequence for an existing gene, `Xsch.v2.MJHO01000004.1.247` (DB: 4,311 bp; new: 3,729 bp). It keeps its name and is in the counts and GRN files, so only `coding_sequence` changes.

Repeat the X. elegans procedure from `notebooks/2025-08-29_remove_outdated_genes.ipynb`, in a new dated notebook `notebooks/YYYY-MM-DD_xs_revised_genes.ipynb`:
1. `db_manager.add_gene_sequence_from_fasta("all_data/to_add/Xsch_47_updated_seqs.fasta", species_id=2)`. It upserts on `gene_name`, so it adds the 46 new genes and updates the sequence of `…04.1.247`.
2. **Waiting on an annotation file.** `db_manager.add_gene_annotations(<blast2go export>, species_id=2, sep=...)`. Check the GO columns have no blanks first: `parse_annotations` doesn't guard against NaN in `GO IDs`/`GO Names`. Until it arrives, the 46 new genes have a sequence but no description or GO terms on the gene info page.
3. **Waiting on confirmation.** `DB().delete_genes_by_names(<22 old names>, dry_run=True)`, review the result, then run it with `dry_run=False`. The ORM cascade removes their annotations, expression, DEG and GRN rows; the old genes have no GRN rows. Not deleting them is harmless: they just have no X. schlechteri seedling expression data.
4. Insert the skipped expression and DEG rows for the 40 genes: re-run the tidy cell filtered to those genes, then use the same bulk-insert code. This only needs step 1, so it can be done now. If Step 2 runs after step 1, the 40 genes are loaded automatically and step 4 isn't needed.

The 22 old names and 40 new names are listed in `Xs_data_questions.md` §3.

**3b (optional):** if a TAIR mapping CSV arrives, run `db_manager.add_a_thaliana_gene_mapping(file)`. It needs the columns `Gene name`, `At Locus ID`, `Wiki gene description`. This enables Arabidopsis search for X. schlechteri.

## Step 4: DB query layer (`database/db.py`)
- `get_experiments_by_species` (:684): query `Experiments` joined to `Species` via `experiments.species_id`, instead of scanning `gene_expressions`.
- `get_gene_expression_data` (:187): the DEG filter join (:208–226) must also match `DifferentialExpression.experiment_id == Experiments.id`. Otherwise a gene with DEG rows in more than one experiment gets duplicated or wrongly filtered rows.
- New helpers so pages list only species with data:
  - `get_species_with_experiments()`
  - `get_species_with_grn()`, via a distinct `Gene.species_id` joined on `RegulatoryInteraction.regulator_gene_id`
- Move the GRN queries out of `server/grn_explorer.py` into `db.py`, and give them a species argument:
  - `get_tf_groups(species_name)`: distinct `regulatory_cluster`, joined to the regulator gene's species, with NULLs filtered out.
  - `get_clusters(tf, species_name, verbose)`: the same species join. **This is required**, because 25+ cluster names (`WRKY:1`, `HSF:1`, …) exist in both species.
  - `get_gene_groups(genes)`: keep it. Gene names are globally unique, so it doesn't need a species argument, but pass the species anyway for clarity.

## Step 5: Frontend
**Shared**
- `utils/constants.py`: replace the single default example `"Xele.ptg000001l.1, Xele.ptg000001l.116"` with a per-species dict, e.g. `EXAMPLE_GENE_IDS = {"X. elegans": ..., "X. schlechteri": "Xsch.v2.MJHO01000001.1.2, Xsch.v2.MJHO01000001.1.9"}`. Pick X. schlechteri genes that have both expression and DEG data.
- Add a species → display-label dict for experiments, or show `Experiments.description` instead of the raw `experiment_name`.

**`server/expression_page.py`**
- Delete the forced reset (:32–33). Use a page-specific session key, `expression_species`, instead of the shared `species` key; that shared key is what clashed with the gene info page.
- Species options = `database.get_species_with_experiments()`, replacing the hard-coded `['X. elegans']` at :38–40.
- When the species changes, reset `input_genes` to that species' example IDs (an `on_change` callback).
- Use the species' example IDs in the instruction text at :270.
- Plots and replicates need no change: labels like `R3b` and `R3_…` only appear in the raw table and CSV, and averaging is per time point. Make the titles (`utils/plots.py:37,76,120`, `f"{treatment}hydration"`) use a `{"De": "Dehydration", "Re": "Rehydration"}` mapping.

**`server/gene_query_page.py`**
- Use its own key, `gene_info_species`, and show per-species example IDs (:36,39,190).
- If the selected species has no Arabidopsis homologues and the user picks an Arabidopsis search type, show an `st.info` explaining this, instead of a silent "0 found".

**`server/grn_explorer.py`**
- Add a species selector (`grn_species`) with options from `get_species_with_grn()`.
- Call the new species-aware `db.py` functions. Their cached wrappers must take `species` as an argument, so the cache key includes it.
- Show a figure and caption per species, via a dict like `GRN_FIGURES = {"X. elegans": ("Fig5_grn.tiff", "Figure 5 …"), "X. schlechteri": ("x_schlechteri_grn.tiff", "<caption from biologist>")}`.
  - Copy `Railplopt_cluster_network_Xs.tiff` to `server/images/x_schlechteri_grn.tiff`.
  - Converting it to PNG is optional; at 2.4 MP it's well under PIL limits.
- Make the text at :144 and :148 use the selected species.
- Fix the bug where the `clusters` tab variable is overwritten by the query result (:135).
- Check whether the `if clusters.open` / `gene_info.open` usage (:125,141) works on the installed Streamlit 1.45.

**`server/home.py`**
- Add a "_X. schlechteri_" tab alongside the X. elegans tab (:36), using the existing `server/images/x_schlechteri_plant.png`. Text and reference come from the biologist; add TODO  until then.
-
## Step 6: Tests (`tests/`, using the existing `temp_db` fixture in `conftest.py`)
Add X. schlechteri fixtures (`Xsch.v2.*` genes) alongside the X. elegans ones, and test:
- `get_experiments_by_species` returns only that species' experiments.
- GRN `get_tf_groups` and `get_clusters` don't mix species when cluster names overlap.
- The DEG-filtered expression query doesn't duplicate rows when a gene has DEG rows in two experiments.
- Regression test: loading a second experiment with the same gene/treatment/time/replicate keeps both experiments' rows (the Step 1 upsert-key fix).

The existing stale tests that call non-existent methods are left to the handover plan.

## Step 7: Release
1. Check the GitHub LFS quota first (HANDOVER_PLAN Phase 6): the DB blob is about 500 MB and will grow.
2. Commit the code changes (migration, `db.py`, pages, tests) separately from the DB.
3. Run the migration and the notebook loads on the real DB, then commit the updated `all_xerophyta_species_db.sqlite` once, via LFS, rather than once per load.
4. Redeploy on Streamlit Cloud and check the shared server, which runs with `fileWatcherType = "none"`, so restart it.

---

## Verification
1. **On a DB copy:** run `alembic upgrade head`. Row counts must be unchanged, `PRAGMA integrity_check` must pass, and `EXPLAIN QUERY PLAN` for expression-by-gene and GRN-by-target must show the indexes being used.
2. **Load on the copy:** expect
   - X. elegans: still 984,942 expression rows, 12,937 DEG rows, 1,825,853 GRN rows
   - X. schlechteri: about 1.86M expression rows, about 13.5k DEG rows, 965,707 GRN rows (adjusted for the biologist's decisions)
   - two experiments, each with a species set
3. `uv run pytest`: the new tests pass.
4. `streamlit run app.py` against the copy, then walk every page in both species:
   - **Expression:** the species switch works and isn't reset, the X. schlechteri experiment appears, example genes plot, the DEG filter works, the raw table shows `R3b`.
   - **Gene info:** X. schlechteri lookup works; Arabidopsis search shows the info message.
   - **GRN:** the X. schlechteri cluster list contains only X. schlechteri clusters, e.g. `WRKY:1` shows only `Xsch` genes; the right figure shows for each species; the gene info tab works.
   - **Home:** the new tab renders.
5. After the Step 3 gene revision: the 22 old names are gone, the 40 new ones have sequence, annotation, expression and DEG rows, and nothing is orphaned (for example, `gene_expressions` rows whose `gene_id` isn't in `genes` = 0).

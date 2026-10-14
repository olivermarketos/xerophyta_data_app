"""
Tests for species-aware queries (expression experiments, DEG filtering, GRN) with more than one species loaded.
"""
import pandas as pd
import pytest
from sqlalchemy import func

import database.db_manager as dbm
import database.models as models
from utils.constants import DEGFilter


@pytest.fixture
def two_species_db(db_instance):
    """X. elegans and X. schlechteri, each with an experiment, expression, DEG and GRN data.
    The GRN cluster names "WRKY:1" and "HSF:1" are used by both species, as in the real data."""
    session = db_instance.session

    xe = models.Species(name="X. elegans")
    xs = models.Species(name="X. schlechteri")
    session.add_all([xe, xs])
    session.flush()

    genes = {name: models.Gene(gene_name=name, species=species) for name, species in [
        ("Xele.1", xe), ("Xele.2", xe), ("Xele.3", xe),
        ("Xsch.1", xs), ("Xsch.2", xs), ("Xsch.3", xs),
    ]}
    session.add_all(genes.values())

    xe_exp = models.Experiments(experiment_name="xe_seedlings_time_course", species=xe)
    xs_exp = models.Experiments(experiment_name="xs_seedlings_time_course", species=xs)
    session.add_all([xe_exp, xs_exp])
    session.flush()

    for gene, experiment, species in [("Xele.1", xe_exp, xe), ("Xsch.1", xs_exp, xs)]:
        for time in (0, 3):
            session.add(models.Gene_expressions(
                treatment="De", time=time, replicate="R1", normalised_expression=1.0, log2_expression=1.0,
                experiment=experiment, species=species, genes=genes[gene],
            ))

    # Xele.1 is up-regulated in its own experiment, and also has a (not DE) row in the other experiment
    session.add_all([
        models.DifferentialExpression(gene=genes["Xele.1"], experiment=xe_exp, de_set="DeT03", de_direction="Up-regulated"),
        models.DifferentialExpression(gene=genes["Xele.1"], experiment=xs_exp),
    ])

    for regulator, target, regulatory_cluster, target_cluster in [
        ("Xele.1", "Xele.2", "WRKY:1", "Cluster e1"),
        ("Xele.1", "Xele.3", "HSF:1", "Cluster e2"),
        ("Xsch.1", "Xsch.2", "WRKY:1", "Cluster s1"),
        ("Xsch.3", "Xsch.2", "MYB:1", "Cluster s2"),
    ]:
        session.add(models.RegulatoryInteraction(
            regulator_gene=genes[regulator], target_gene=genes[target],
            regulatory_cluster=regulatory_cluster, target_cluster=target_cluster, direction="Activation",
        ))

    session.commit()
    return db_instance


class TestExperimentsBySpecies:
    def test_returns_only_that_species_experiments(self, two_species_db):
        assert [e.experiment_name for e in two_species_db.get_experiments_by_species("X. elegans")] == ["xe_seedlings_time_course"]
        assert [e.experiment_name for e in two_species_db.get_experiments_by_species("X. schlechteri")] == ["xs_seedlings_time_course"]

    def test_species_with_experiments(self, two_species_db):
        assert [s.name for s in two_species_db.get_species_with_experiments()] == ["X. elegans", "X. schlechteri"]


class TestDEGFilter:
    def test_deg_filter_does_not_duplicate_rows_across_experiments(self, two_species_db):
        data = two_species_db.get_gene_expression_data(["Xele.1"], "xe_seedlings_time_course", DEGFilter.SHOW_DEG)
        assert len(data) == 2  # one row per time point, not one per DEG row

    def test_deg_filter_uses_the_selected_experiment(self, two_species_db):
        data = two_species_db.get_gene_expression_data(["Xele.1"], "xe_seedlings_time_course", DEGFilter.SHOW_UP)
        assert len(data) == 2
        data = two_species_db.get_gene_expression_data(["Xele.1"], "xe_seedlings_time_course", DEGFilter.SHOW_DOWN)
        assert data.empty


class TestGRN:
    def test_species_with_grn(self, two_species_db):
        assert [s.name for s in two_species_db.get_species_with_grn()] == ["X. elegans", "X. schlechteri"]

    def test_tf_groups_are_per_species(self, two_species_db):
        assert two_species_db.get_tf_groups("X. elegans") == ["HSF:1", "WRKY:1"]
        assert two_species_db.get_tf_groups("X. schlechteri") == ["MYB:1", "WRKY:1"]

    def test_shared_cluster_name_does_not_mix_species(self, two_species_db):
        targets = two_species_db.get_tf_group_targets("WRKY:1", "X. schlechteri")
        assert targets["target_cluster"].tolist() == ["Cluster s1"]

        verbose = two_species_db.get_tf_group_targets("WRKY:1", "X. schlechteri", verbose=True)
        assert verbose["regulator_genes"].tolist() == ["Xsch.1"]
        assert verbose["target_genes"].tolist() == ["Xsch.2"]

    def test_gene_grn_clusters(self, two_species_db):
        groups = two_species_db.get_gene_grn_clusters(["Xsch.1", "Xsch.2"], "X. schlechteri")
        assert groups["Xsch.1"] == {"target_clusters": [], "regulatory_clusters": ["WRKY:1"]}
        assert sorted(groups["Xsch.2"]["target_clusters"]) == ["Cluster s1", "Cluster s2"]


class TestArabidopsisHomologues:
    def test_has_arabidopsis_homologues(self, two_species_db):
        session = two_species_db.session
        gene = session.query(models.Gene).filter_by(gene_name="Xele.1").one()
        gene.arabidopsis_homologues.append(models.ArabidopsisHomologue(a_thaliana_locus="AT1G01010"))
        session.commit()

        assert two_species_db.has_arabidopsis_homologues("X. elegans")
        assert not two_species_db.has_arabidopsis_homologues("X. schlechteri")


def test_add_rna_seq_data_keeps_rows_from_other_experiments(two_species_db):
    """Regression test: the upsert key used to ignore the experiment, so loading a second experiment
    overwrote rows of the first one with the same gene/treatment/time/replicate."""
    dbm.add_experiment("xe_second_experiment")
    rows = pd.DataFrame({
        "gene_name": ["Xele.1", "Xele.1"],
        "treatment": ["De", "De"],
        "time": [0, 3],
        "replicate": ["R1", "R1"],
        "normalised_expression": [5.0, 5.0],
        "log2_expression": [2.6, 2.6],
    })
    dbm.add_rna_seq_data(rows, "X. elegans", "xe_second_experiment")

    rows_per_experiment = dict(
        two_species_db.session.query(models.Experiments.experiment_name, func.count(models.Gene_expressions.id))
        .join(models.Gene_expressions)
        .group_by(models.Experiments.experiment_name)
        .all()
    )
    assert rows_per_experiment["xe_seedlings_time_course"] == 2
    assert rows_per_experiment["xe_second_experiment"] == 2

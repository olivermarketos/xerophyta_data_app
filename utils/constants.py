from enum import Enum

class DEGFilter(Enum):
    SHOW_ALL = 1
    SHOW_DEG = 2
    SHOW_UP = 3
    SHOW_DOWN = 4

DEG_FILTER_OPTIONS = {
    "Show all genes": DEGFilter.SHOW_ALL,
    "Show all differentially expressed genes": DEGFilter.SHOW_DEG,
    "Show only up-regulated genes": DEGFilter.SHOW_UP,
    "Show only down-regulated genes": DEGFilter.SHOW_DOWN,
}

GENE_SELECTION_OPTIONS = {
    "Xerophyta GeneID": {
        "placeholder": "Xele.ptg000001l.1, Xele.ptg000001l.116",
        "key": "Gene_ID",
        "input_label": "Enter Xerophyta GeneIDs separated by commas, space or newline:"
    },
    "Arabidopsis homologue locus": {
        "placeholder": "At4g32010, At5g67620, AT3G13850",
        "key": "Arab_loci",
        "input_label": "Enter Arabidopsis orthologues separated by commas, space or newline:"
    },
    "Arabidopsis homologue common name": {
        "placeholder": "glyoxylate reductase 2, OXA1",
        "key": "Arab_common_name",
        "input_label": "Enter Arabidopsis orthologues separated by commas, space or newline:"
    },
    "Genes with GO term": {
        "key": "GO_term",
        "placeholder": "immune system process, leaf senescence, GO:0005515",
        "input_label": "Enter GO term description or ID (GO:xxx) separated by commas or newline:"
    }
}
import re 
import database.db as db





def parse_input(input):
    """
    Splits the user's input (comma, space, newline) into a list of unique, non-empty strings.
        input: str: The user's input eg. gene names, GO terms...
        tokens: list: A list of unique, non-empty strings.
    """
    if not input.strip():
        return []
    # Replace commas/newlines with spaces
    cleaned = input.replace("\n", ",")
    # Split on comma
    tokens = list(set([t.strip() for t in cleaned.split(",") if t.strip()]))
    # Return unique tokens
    return tokens

def retreive_query_data(input_genes,selected_species, gene_input_type):
    database = db.DB()
    annotation_data = []
    matched_input = set()
    missing_input = set()

    if gene_input_type == "Gene_ID":
        annotation_data = database.get_gene_annotation_data(input_genes, "xerophyta_gene_name",selected_species)
    
        if annotation_data:
            matched_input = {gene.gene_name.lower() for gene in annotation_data}
        else:
            matched_input = set()
        missing_input = {gene for gene in input_genes if gene.lower() not in matched_input}

    elif gene_input_type == "Arab_loci":
        annotation_data = database.get_gene_annotation_data(input_genes, "a_thaliana_locus",selected_species)
    
        if annotation_data:
            matched_input = {gene.arabidopsis_homologues[0].a_thaliana_locus.lower() for gene in annotation_data}
        
        else:
            matched_input = set()
        
        missing_input = {gene for gene in input_genes if gene.lower() not in matched_input}


    elif gene_input_type == "Arab_common_name":
        annotation_data = database.get_gene_annotation_data(input_genes, "a_thaliana_common_name",selected_species)

        if annotation_data:
            # Determine which search terms did not match any homologues
            for gene in annotation_data:
                for homologue in gene.arabidopsis_homologues:
                    common_name = homologue.a_thaliana_common_name.lower()
                    for term in input_genes:
                        if term.lower() in common_name:
                            matched_input.add(term)

        missing_input = [term for term in input_genes if term not in matched_input]

    elif gene_input_type == "GO_id":
        annotation_data = database.get_gene_annotation_data(input_genes, "go_id",selected_species)
        
        normalized_inputs = {database.normalize_go_term(term) for term in input_genes}

        if annotation_data:
            for gene in annotation_data:
                for annotation in gene.annotations:
                    for go in annotation.go_ids:
                        normalized_go = database.normalize_go_term(go.go_id)
                        # Check for partial match: if either string contains the other.
                        # print(f'normalized_go: {normalized_go}')
                        for user_term in normalized_inputs:
                            if user_term in normalized_go:
                                matched_input.add(normalized_go)

        else:
            matched_input = set()
        missing_input = normalized_inputs - matched_input

    elif gene_input_type == "GO_name":
        annotation_data = database.get_gene_annotation_data(input_genes, "go_name",selected_species)
        if annotation_data:
            for gene in annotation_data:
                for annotation in gene.annotations:
                    # iterate over GO objects via the go_ids relationship
                    for go in annotation.go_ids:
                        # Ensure go.go_name exists and normalize it to lowercase
                        go_name = go.go_name.lower() if go.go_name else ""
                        for term in input_genes:
                            # Check if the lowercase search term is in the GO name
                            if term.lower() in go_name:
                                matched_input.add(term)
        missing_input = [term for term in input_genes if term.lower() not in {m.lower() for m in matched_input}]

    elif gene_input_type == "EC_code":
        annotation_data = database.get_gene_annotation_data(input_genes, "enzyme_code",selected_species)
        
        matched_input = set()
        normalized_inputs = {term for term in input_genes}
        if annotation_data:
            for gene in annotation_data:
                for annotation in gene.annotations:
                    for enzyme_code in annotation.enzyme_codes:
                        for user_term in input_genes:
                            if user_term in enzyme_code.enzyme_code:
                                matched_input.add(enzyme_code.enzyme_code)
                        

        else:
            matched_input = set()
        missing_input = normalized_inputs - matched_input
    
    elif gene_input_type == "EC_name":
        annotation_data = database.get_gene_annotation_data(input_genes, "enzyme_name",selected_species)
        if annotation_data:
            for gene in annotation_data:
                for annotation in gene.annotations:
                    # iterate over GO objects via the go_ids relationship
                    for enzyme in annotation.enzyme_codes:
                        # Ensure go.go_name exists and normalize it to lowercase
                        enzyme_name = enzyme.enzyme_name.lower() if enzyme.enzyme_name else ""
                        for term in input_genes:
                            # Check if the lowercase search term is in the GO name
                            if term.lower() in enzyme_name:
                                matched_input.add(term)
        missing_input = [term for term in input_genes if term.lower() not in {m.lower() for m in matched_input}]

    return annotation_data, matched_input, missing_input
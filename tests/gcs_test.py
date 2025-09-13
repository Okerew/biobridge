from collections import Counter


def punnett_square(parent1, parent2):
    # Generate all possible allele combinations for the children
    offspring_combinations = [
        p1 + p2 for p1 in parent1 for p2 in parent2
    ]

    # Normalize the offspring combinations (AA, Aa are the same as Aa, AA)
    normalized_offspring = [''.join(sorted(offspring)) for offspring in offspring_combinations]

    # Count occurrences of each genotype
    genotype_counts = Counter(normalized_offspring)

    # Calculate probabilities
    total_offspring = sum(genotype_counts.values())
    genotype_probabilities = {genotype: count / total_offspring for genotype, count in genotype_counts.items()}

    return genotype_probabilities

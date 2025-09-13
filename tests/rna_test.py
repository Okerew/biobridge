from biobridge.genes.rna import RNA

def test_rna_class():
    # Test RNA initialization
    rna_sequence = "AUGGCCAUGGCGCCCAGAACUGAGAUCAAUAGUACCCGUAUUAACGGGUGA"
    rna = RNA(rna_sequence)
    print("Initial RNA:")
    print(rna)

    # Test adding genes
    rna.add_gene("Gene1", 0, 9)
    rna.add_gene("Gene2", 12, 21)
    print("\nRNA after adding genes:")
    print(rna)

    # Test mutation
    print("\nTesting mutation:")
    rna.mutate(3, 'G')
    print(rna)

    # Test random mutation
    print("\nTesting random mutation:")
    rna.random_mutate()
    print(rna)

    # Test reverse transcription
    dna_sequence = rna.reverse_transcribe()
    print("\nReverse transcribed DNA:")
    print(dna_sequence)

    # Test translation
    protein_sequence = rna.translate()
    print("\nTranslated protein sequence:")
    print(protein_sequence)

    # Test invalid gene addition
    print("\nTesting invalid gene addition:")
    rna.add_gene("InvalidGene", 100, 110)

    # Test mutation with invalid index
    print("\nTesting mutation with invalid index:")
    rna.mutate(100, 'A')

if __name__ == "__main__":
    test_rna_class()
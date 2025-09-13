from biobridge.tools.crispr import CRISPR
from biobridge.genes.dna import DNA
dna = DNA("ATCGATCGATCGATCGATCG")
crispr = CRISPR("ATCG")
edited_dna = crispr.edit_genome(dna, 'insert', 'GGG')
edited_dna = crispr.simulate_off_target_effects(edited_dna)
print(edited_dna.sequence)
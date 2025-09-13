from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell, ChromosomePair
from biobridge.genes.chromosome import Chromosome, DNA

dna1 = DNA("ATCG" * 100)
dna2 = DNA("GCTA" * 100)
chromosome1 = Chromosome(DNA("ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"), "1")
chromosome2 = Chromosome(dna2, "1")
chromosome_pairs = [ChromosomePair(chromosome1, chromosome2)]
eukaryotic_cell = EukaryoticCell("EukaryoticCell1", cell_type="stem_cell", chromosome_pairs=chromosome_pairs)
print(eukaryotic_cell.describe())
eukaryotic_cell.visualize_cell()
print(eukaryotic_cell.to_json())
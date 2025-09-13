from biobridge.tools.dna_analyzer import DNAAnalyzer
from biobridge.genes.dna import DNA

dna = DNA("ATGCGTACTGATCGTACGATCGTAGCTAGCTAGCGTAGCTGATCGTACG")
analyzer = DNAAnalyzer(dna)

# Generate a comprehensive genetic analysis report
report = analyzer.generate_comprehensive_report()
print(report)

# Or analyze specific aspects
hemophilia_markers = analyzer.detect_hemophilia_markers()
color_blindness_markers = analyzer.detect_color_blindness_markers()
gene_interactions = analyzer.analyze_gene_interactions()

trait_probabilities, detected_traits = analyzer.detect_traits()
print(trait_probabilities)

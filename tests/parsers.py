import unittest
from biobridge.blocks.protein import Protein
from biobridge.genes.dna import DNA
from biobridge.parsers.genbank import GenbankParser
from biobridge.parsers.fasta import FastaParser


class TestParsers(unittest.TestCase):

    def setUp(self):
        # Sample data for each format
        self.genbank_data = """
LOCUS       SCU49845     5028 bp    DNA             PLN       21-JUN-1999
DEFINITION  Saccharomyces cerevisiae TCP1-beta gene, partial cds, and Axl2p
            (AXL2) and Rev7p (REV7) genes, complete cds.
ACCESSION   U49845
VERSION     U49845.1  GI:1293613
KEYWORDS    .
SOURCE      Saccharomyces cerevisiae (baker's yeast)
  ORGANISM  Saccharomyces cerevisiae
            Eukaryota; Fungi; Ascomycota; Saccharomycotina; Saccharomycetes;
            Saccharomycetales; Saccharomycetaceae; Saccharomyces.
REFERENCE   1  (bases 1 to 5028)
  AUTHORS   Torpey,L.E., Gibbs,P.E., Nelson,J. and Lawrence,C.W.
  TITLE     Cloning and sequence of REV7, a gene whose function is required for
            DNA damage-induced mutagenesis in Saccharomyces cerevisiae
  JOURNAL   Yeast 10 (11), 1503-1509 (1994)
  PUBMED    7871890
FEATURES             Location/Qualifiers
     source          1..5028
                     /organism="Saccharomyces cerevisiae"
                     /db_xref="taxon:4932"
                     /chromosome="IX"
                     /map="9"
     CDS             <1..206
                     /codon_start=3
                     /product="TCP1-beta"
                     /protein_id="AAA98665.1"
                     /translation="SSIYNGISTSGLDLNNGTIADMRQLGIVESYKLKRAVVSSASEA
                     AEVLLRVDNIIRARPRTANRQHM"
ORIGIN
        1 gatcctccat atacaacggt atctccacct caggtttaga tctcaacaac ggaaccattg
       61 ccgacatgag acagttaggt atcgtcgaga gttacaagct aaaacgagca gtagtcagct
      121 ctgcatctga agccgctgaa gttctactaa gggtggataa catcatccgt gcaagaccaa
//
"""

        self.fasta_data = """>sp|P0ADF8|ACEA_ECOLI Isocitrate lyase OS=Escherichia coli (strain K12) OX=83333 GN=aceA PE=1 SV=2
MKTRTQQIEDLVKELVDRDVQEVVLSAETMWKETVKHIGAQPSWSQEAIRDGEKWRMKL
ALAELTGIPPPLINGTPLDDVVAEVRRLCEEHQLQFMVLNPGQTDGTWTIEEALKHTTP
VTFVEWAEKQGAAASIAKAIASDRAGYLEYERNRHVREFTQQGAITDDEANEQVCEIVA
KGDIADAFSFGEQVMHHYEAPLRDHIRADFRDPNKIAVALKEFLEASRKADARRCRYDG
TDIAYWDEHAIPFGKIDAHLFDICQFTNTGPLRGLLGEDPWSAEPFKTQGCGGIFDMYA
ACGNRLDAERTEIHQGDDAFFPFTGAWIPRIAEILKERYKEYIKEHNKNIAPEHRLAW
LELTTYNRERRRLASEYDIVPIVDEAGRLKAVDESVVAEEARRLLRMHGLDENTIGGTC
VGVLPGATRGRIVETETDDLTAFNRGDLTHWVYKKDAPRLLKTLTFEDGGYASNGH
"""

    def test_genbank_parser(self):
        with open('test_genbank.gb', 'w') as f:
            f.write(self.genbank_data)

        parser = GenbankParser('test_genbank.gb')
        elements = parser.parse_records()
        metadata = parser.get_metadata()

        self.assertTrue(any(isinstance(elem, DNA) for elem in elements))
        self.assertEqual(len(metadata), 1)


    def test_fasta_parser(self):
        with open('test_fasta.fasta', 'w') as f:
            f.write(self.fasta_data)

        parser = FastaParser('test_fasta.fasta')
        elements = parser.parse_records()
        metadata = parser.get_metadata()

        self.assertEqual(len(elements), 1)
        self.assertIsInstance(elements[0], Protein)
        self.assertEqual(len(metadata), 1)
        self.assertTrue(metadata[0]['id'].startswith('sp|P0ADF8|ACEA_ECOLI'))

if __name__ == '__main__':
    unittest.main()

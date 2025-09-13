from biobridge.tools.pcr import PCR

dna_sequence = "ATGCATGCATGCATGCATGC"
forward_primer = "ATGC"
reverse_primer = "GCAT"

pcr = PCR(dna_sequence, forward_primer, reverse_primer)
amplified_sequences = pcr.amplify()

print("Amplified Sequences:")
for seq in amplified_sequences:
    print(seq)
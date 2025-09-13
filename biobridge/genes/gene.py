class Gene:
    def __init__(self, name, start, end, inheritance='mixed'):
        self.name = name
        self.start = start
        self.end = end
        self.set_inheritance(inheritance)

    def set_inheritance(self, inheritance):
        valid_inheritances = ['recessive', 'dominant', 'mixed']
        if inheritance.lower() in valid_inheritances:
            self.inheritance = inheritance.lower()
        else:
            raise ValueError(f"Invalid inheritance type. Must be one of {valid_inheritances}")

    def to_dict(self):
        return {
            'gene_name': self.name,
            'start': self.start,
            'end': self.end,
            'inheritance': self.inheritance
        }

    def from_dict(self, gene_dict):
        self.name = gene_dict['gene_name']
        self.start = gene_dict['start']
        self.end = gene_dict['end']
        self.set_inheritance(gene_dict['inheritance'])

    def __str__(self):
        return f"Gene: {self.name}, Position: {self.start}-{self.end}, Inheritance: {self.inheritance}"

    def __repr__(self):
        return self.__str__()

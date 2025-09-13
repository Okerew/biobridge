from biobridge.definitions.proteins.enzyme import EnzymeProtein
from biobridge.definitions.proteins.structural import StructuralProtein
from biobridge.definitions.proteins.signaling import SignalingProtein
from biobridge.definitions.proteins.transport import TransportProtein
from biobridge.definitions.proteins.hemoglobin import Hemoglobin
from biobridge.blocks.cell import Cell

enzyme = EnzymeProtein("Amylase", "MFVLRVLVCL...", "starch", "maltose")
structural = StructuralProtein("Collagen", "GPPGPAGPPGPV...", "extracellular matrix")
signaling = SignalingProtein("Insulin", "MALWMRLLPL...", "glucose uptake")
transport = TransportProtein("GLUT4", "MPSGFQQIGSEDGEPPQQRVTGTL...", "glucose")
hemoglobin = Hemoglobin("Hemoglobin", "VHLTPEEK", "H")

cell = Cell("Liver cell")
hemoglobin.bind_oxygen(3)
print(enzyme.interact_with_cell(cell))
print(structural.interact_with_cell(cell))
print(signaling.interact_with_cell(cell))
print(transport.interact_with_cell(cell))
print(hemoglobin.interact_with_cell(cell))

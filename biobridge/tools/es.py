import math
import random
from enum import Enum
from typing import List, Tuple

import pygame

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
from biobridge.definitions.organ import Organ
from biobridge.networks.system import System


class DevelopmentalStage(Enum):
    Zygote = 0
    Cleavage = 1
    Blastula = 2
    Gastrula = 3
    Organogenesis = 4
    Fetus = 5


class EmbryoSimulation:
    def __init__(self, initialCells: int = 1):
        self.cells: List[Cell] = []
        self.tissues: List[Tissue] = []
        self.organs: List[Organ] = []
        self.systems: List[System] = []
        self.stage: DevelopmentalStage = DevelopmentalStage.Zygote
        self.daysPassed: int = 0
        self.rng = random.Random()

        self.initialize_pygame()
        self.initialize_simulation(initialCells)

    def initialize_pygame(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Embryo Simulation")
        self.font = pygame.font.SysFont(None, 20)

    def initialize_simulation(self, initialCells: int):
        self.cells = [Cell("Zygote_" + str(i), "Zygote") for i in range(initialCells)]

    def getCells(self):
        return self.cells

    def getTissues(self):
        return self.tissues

    def getOrgans(self):
        return self.organs

    def getSystems(self):
        return self.systems

    def getStage(self):
        return self.stage

    def step(self):
        self.daysPassed += 1
        if self.stage == DevelopmentalStage.Zygote and self.daysPassed >= 1:
            self.stage = DevelopmentalStage.Cleavage
        elif self.stage == DevelopmentalStage.Cleavage:
            self.divideCells()
            if len(self.cells) >= 32:
                self.stage = DevelopmentalStage.Blastula
        elif self.stage == DevelopmentalStage.Blastula:
            self.formBlastula()
            if self.daysPassed >= 5:
                self.stage = DevelopmentalStage.Gastrula
        elif self.stage == DevelopmentalStage.Gastrula:
            self.initiateGastrulation()
            self.differentiateGermLayers()
            if self.daysPassed >= 14:
                self.stage = DevelopmentalStage.Organogenesis
        elif self.stage == DevelopmentalStage.Organogenesis:
            self.initiateOrganogenesis()
            if self.daysPassed >= 56:
                self.stage = DevelopmentalStage.Fetus
        elif self.stage == DevelopmentalStage.Fetus:
            self.developFetus()
            self.developSystems()

        for tissue in self.tissues:
            pass  # Placeholder for tissue simulation

        for organ in self.organs:
            if self.rng.random() < 0.05:
                organ.heal(self.rng.uniform(0, 5))
            if self.rng.random() < 0.02:
                pass  # Placeholder for damage simulation

        for system in self.systems:
            system.simulate_time_step()

    def run(self, steps: int):
        running = True
        while running and steps > 0:
            self.step()
            self.visualize()
            steps -= 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    def divideCells(self):
        newCells = []
        for cell in self.cells:
            if self.rng.random() < 0.8:
                newCells.append(cell.divide())
        self.cells.extend(newCells)

    def formBlastula(self):
        if not self.tissues:
            trophoblast = Tissue("Trophoblast", "Epithelial")
            inner_cell_mass = Tissue("Inner Cell Mass", "Pluripotent")
            self.tissues.extend([trophoblast, inner_cell_mass])

            for cell in self.cells:
                if self.rng.random() < 0.7:
                    trophoblast.add_cell(cell)
                    cell.cell_type = "Trophoblast"
                else:
                    inner_cell_mass.add_cell(cell)
                    cell.cell_type = "Inner Cell Mass"

    def initiateGastrulation(self):
        if len(self.tissues) == 2:
            germ_layers = ["Ectoderm", "Mesoderm", "Endoderm"]
            germ_layer_tissues = [Tissue(layer, "Epithelial") for layer in germ_layers]
            self.tissues.extend(germ_layer_tissues)

            icm_cells = self.tissues[1].cells
            for cell in icm_cells:
                layer_index = self.rng.randint(0, 2)
                germ_layer_tissues[layer_index].add_cell(cell)

            self.tissues.pop(1)  # Remove Inner Cell Mass tissue

    def differentiateGermLayers(self):
        for tissue in self.tissues:
            for cell in tissue.cells:
                if tissue.name == "Ectoderm":
                    cell.cell_type = self.rng.choice(["Neuron", "Epidermis"])
                elif tissue.name == "Mesoderm":
                    cell.cell_type = self.rng.choice(["Muscle", "Bone"])
                elif tissue.name == "Endoderm":
                    cell.cell_type = self.rng.choice(["Intestinal", "Lung"])

    def initiateOrganogenesis(self):
        if not self.organs:
            organNames = ["Brain", "Heart", "Liver", "Lungs", "Kidneys"]
            for name in organNames:
                organ_tissues = [
                    Tissue(f"{name}_Tissue_{i}", "Specialized") for i in range(3)
                ]
                organ = Organ(name, organ_tissues)
                self.organs.append(organ)

            for tissue in self.tissues:
                for cell in tissue.cells:
                    if self.rng.random() < 0.3:
                        organ_index = self.rng.randint(0, len(self.organs) - 1)
                        organ_tissue_index = self.rng.randint(0, 2)
                        organ_tissue = self.organs[organ_index].tissues[
                            organ_tissue_index
                        ]
                        organ_tissue.add_cell(cell)
                        cell.cell_type = f"{self.organs[organ_index].name} Cell"

    def developFetus(self):
        for organ in self.organs:
            for tissue in organ.tissues:
                if self.rng.random() < 0.1:
                    tissue.cells.append(Cell(f"{organ.name}_New", f"{organ.name} Cell"))
            if self.rng.random() < 0.05:
                pass  # Placeholder for organ growth

    def developSystems(self):
        if not self.systems:
            systemNames = [
                "Nervous System",
                "Circulatory System",
                "Respiratory System",
                "Digestive System",
                "Immune System",
            ]
            self.systems = [System(name) for name in systemNames]

            for organ in self.organs:
                if organ.name == "Brain" or organ.name == "Spinal Cord":
                    self.systems[0].add_organ(organ)
                elif organ.name == "Heart" or organ.name == "Blood Vessels":
                    self.systems[1].add_organ(organ)
                elif organ.name == "Lungs":
                    self.systems[2].add_organ(organ)
                elif organ.name == "Stomach" or organ.name == "Intestines":
                    self.systems[3].add_organ(organ)
                elif organ.name == "Thymus" or organ.name == "Lymph Nodes":
                    self.systems[4].add_organ(organ)

        for system in self.systems:
            system.simulate_time_step()

    def visualize(self):
        self.window.fill((255, 255, 255))  # White background

        cell_radius = 5
        spacing = 15
        cells_per_row = int(math.sqrt(len(self.cells)))
        all_cells = []

        # Collect cells from all tissues and organs
        for tissue in self.tissues:
            all_cells.extend(tissue.cells)
        for organ in self.organs:
            for tissue in organ.tissues:
                all_cells.extend(tissue.cells)

        # Draw cells
        for i, cell in enumerate(all_cells):
            x_pos = spacing + (i % cells_per_row) * spacing
            y_pos = spacing + (i // cells_per_row) * spacing
            cell_color = self.get_cell_color(cell.cell_type)
            pygame.draw.circle(self.window, cell_color, (x_pos, y_pos), cell_radius)

        # Draw stage and cell count information
        text_start_y = self.window.get_height() * 0.7
        stage_text = f"Stage: {self.stage.name} | Day: {self.daysPassed}"
        cell_count_text = f"Total Cells: {len(all_cells)}"

        stage_surface = self.font.render(stage_text, True, (0, 0, 0))
        cell_count_surface = self.font.render(cell_count_text, True, (0, 0, 0))

        self.window.blit(stage_surface, (10, text_start_y))
        self.window.blit(cell_count_surface, (10, text_start_y + 30))

        # Draw organ and system information
        y_pos = text_start_y + 60
        x_pos = 10
        items_per_column = 5
        current_item = 0

        for organ in self.organs:
            organ_health = organ.get_health()
            organ_info = f"{organ.name}: {int(organ_health)}%"
            info_surface = self.font.render(organ_info, True, (0, 0, 0))
            self.window.blit(info_surface, (x_pos, y_pos))
            current_item += 1
            if current_item % items_per_column == 0:
                x_pos += 200
                y_pos = text_start_y + 60
            else:
                y_pos += 20

        for system in self.systems:
            system_status = 1.0  # Placeholder for system status
            system_info = f"{system.name}: {int(system_status * 100)}%"
            info_surface = self.font.render(system_info, True, (0, 0, 0))
            self.window.blit(info_surface, (x_pos, y_pos))
            current_item += 1
            if current_item % items_per_column == 0:
                x_pos += 200
                y_pos = text_start_y + 60
            else:
                y_pos += 20

        pygame.display.flip()

    def get_cell_color(self, cell_type: str) -> Tuple[int, int, int]:
        colors = {
            "Zygote": (255, 255, 0),  # Yellow
            "Inner Cell Mass": (255, 255, 0),  # Yellow
            "Trophoblast": (0, 255, 255),  # Cyan
            "Neuron": (0, 0, 255),  # Blue
            "Epidermis": (0, 0, 255),  # Blue
            "Muscle": (255, 0, 0),  # Red
            "Bone": (255, 0, 0),  # Red
            "Intestinal": (0, 255, 0),  # Green
            "Lung": (0, 255, 0),  # Green
            "Brain Cell": (128, 0, 128),  # Purple
            "Liver Cell": (165, 42, 42),  # Brown
            "Kidney Cell": (255, 140, 0),  # Dark orange
        }
        return colors.get(cell_type, (255, 255, 255))  # Default to white

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

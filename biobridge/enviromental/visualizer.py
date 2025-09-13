from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

# Cell data type
CellData = Dict[str, Any]


class Visualizer:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.window_width = width
        self.window_height = height
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cell Environment Visualizer")

        # Font setup
        self.font = pygame.font.SysFont("Arial", 12)

        # Store for cell graphics
        self.cells: Dict[int, Tuple[pygame.Rect, str]] = {}
        self.cellPositions: Dict[int, Tuple[int, int]] = {}
        self.selectedCellId: Optional[int] = None
        self.m_moveCell: Optional[Callable[[int, int, int], None]] = None

    def update(self, cell_data: List[CellData]):
        """Update cell visual representation based on cell_data."""
        self.cells.clear()
        self.cellPositions.clear()

        for cell in cell_data:
            x = cell["x"]
            y = cell["y"]
            health = cell["health"]
            cell_type = cell["type"]
            cell_id = cell["id"]

            # Create a circle-like rectangle
            rect = pygame.Rect(x * 20, y * 20, 20, 20)
            color = (255, int(health * 2.55), 0)  # Color based on health
            self.cells[cell_id] = (rect, cell_type)
            self.cellPositions[cell_id] = (x, y)

    def run_once(self) -> bool:
        """Render cells and handle events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos[0] // 20, event.pos[1] // 20
                self.selectCell(x, y)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                x, y = event.pos[0] // 20, event.pos[1] // 20
                self.moveSelectedCell(x, y)

        self.window.fill((0, 0, 0))  # Clear screen to black

        # Draw cells
        for cell_id, (rect, cell_type) in self.cells.items():
            pygame.draw.rect(
                self.window, (255, int(2.55 * 100), 0), rect
            )  # Green cell for demo
            text_surface = self.font.render(cell_type, True, (255, 255, 255))
            self.window.blit(text_surface, (rect.x, rect.y + 20))

        pygame.display.flip()  # Update display
        return True

    def selectCell(self, x: int, y: int):
        """Select a cell at position (x, y) if one exists."""
        for cell_id, (rect, _) in self.cells.items():
            if rect.x // 20 == x and rect.y // 20 == y:
                self.selectedCellId = cell_id
                return
        self.selectedCellId = None

    def moveSelectedCell(self, x: int, y: int):
        """Move the selected cell to a new position (x, y)."""
        if self.selectedCellId is not None and self.m_moveCell:
            self.m_moveCell(self.selectedCellId, x, y)
            # Update the visual position (for immediate visual feedback)
            for cell_id, (rect, _) in self.cells.items():
                if cell_id == self.selectedCellId:
                    rect.x, rect.y = x * 20, y * 20
                    self.cellPositions[self.selectedCellId] = (x, y)
                    break

    def setMoveCell(self, func: Callable[[int, int, int], None]):
        """Set the callback function to handle cell movements."""
        self.m_moveCell = func

    def getCellPositions(self) -> Dict[int, Tuple[int, int]]:
        """Return current cell positions."""
        return self.cellPositions.copy()

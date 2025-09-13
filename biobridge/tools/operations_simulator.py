import random
import time
from typing import Any, Dict

import pygame


class SurgicalTool:
    def __init__(self, name: str, precision: float, damage: float):
        self.name = name
        self.precision = precision
        self.damage = damage

    def get_name(self) -> str:
        return self.name

    def get_precision(self) -> float:
        return self.precision

    def get_damage(self) -> float:
        return self.damage


class OperationResult:
    def __init__(self, success: bool, message: str, health_change: float):
        self.success = success
        self.message = message
        self.health_change = health_change

    def get_success(self) -> bool:
        return self.success

    def get_message(self) -> str:
        return self.message

    def get_health_change(self) -> float:
        return self.health_change


class OperationTarget:
    def __init__(self, name: str, health: float):
        self.name = name
        self.health = health

    def get_name(self) -> str:
        return self.name

    def get_health(self) -> float:
        return self.health

    def set_health(self, new_health: float) -> None:
        self.health = new_health


class SurgicalSimulator:
    def __init__(self):
        self.tools = {
            "scalpel": SurgicalTool("Scalpel", 0.9, 5.0),
            "forceps": SurgicalTool("Forceps", 0.95, 1.0),
            "suture": SurgicalTool("Suture", 0.85, 2.0),
            "laser": SurgicalTool("Laser", 0.8, 10.0),
            "electrocautery": SurgicalTool("Electrocautery", 0.75, 8.0),
            "harmonic_scalpel": SurgicalTool("Harmonic Scalpel", 0.85, 7.0),
        }
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 24)

    def operate(self, target: OperationTarget, tool_name: str) -> OperationResult:
        if tool_name not in self.tools:
            return OperationResult(False, "Unknown tool", 0.0)

        tool = self.tools[tool_name]
        success = random.random() < tool.get_precision()
        health_change = -tool.get_damage() if success else tool.get_damage()
        target.set_health(target.get_health() + health_change)

        message = f"{'Operation successful' if success else 'Operation failed'}. Used {tool.get_name()}."
        return OperationResult(success, message, health_change)

    def print_operation(self, target: OperationTarget, tool_name: str) -> None:
        print(f"Operating on {target.get_name()} with {tool_name}")
        print(f"Initial health: {target.get_health()}")

        for _ in range(10):
            print(".", end="", flush=True)
            time.sleep(0.2)

        print()
        result = self.operate(target, tool_name)
        print(result.get_message())
        print(f"Health change: {result.get_health_change()}")
        print(f"Final health: {target.get_health()}")

    def visualize_operation(self, target: OperationTarget) -> None:
        window_width, window_height = 1024, 768
        window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Da Vinci Surgical Simulator Enhanced")

        status_text = ""
        current_tool = "scalpel"
        is_operating = False

        health_bar_width = 200
        health_bar_height = 30

        cursor_pos = (0, 0)

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_tool = "scalpel"
                    elif event.key == pygame.K_2:
                        current_tool = "forceps"
                    elif event.key == pygame.K_3:
                        current_tool = "suture"
                    elif event.key == pygame.K_4:
                        current_tool = "laser"
                    elif event.key == pygame.K_5:
                        current_tool = "electrocautery"
                    elif event.key == pygame.K_6:
                        current_tool = "harmonic_scalpel"
                    elif event.key == pygame.K_SPACE:
                        is_operating = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        is_operating = False

            if is_operating:
                result = self.operate(target, current_tool)
                status_text = f"{result.get_message()}\nHealth: {target.get_health()}"

            cursor_pos = pygame.mouse.get_pos()

            # Drawing
            window.fill((50, 50, 50))

            # Health bar background
            pygame.draw.rect(
                window, (0, 0, 0), (20, 70, health_bar_width, health_bar_height)
            )

            # Health bar
            health_bar_width_current = max(
                0, min(health_bar_width, target.get_health() * 2)
            )
            pygame.draw.rect(
                window,
                (0, 255, 0),
                (20, 70, health_bar_width_current, health_bar_height),
            )

            # Operation area
            pygame.draw.circle(window, (255, 0, 0), (424, 350), 150)  # Red circle

            # Render status text
            status_surface = self.font.render(status_text, True, (255, 255, 255))
            window.blit(status_surface, (20, 20))

            # Render cursor
            pygame.draw.circle(window, (255, 255, 255), cursor_pos, 10)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def visualize_training_mode(self, target: OperationTarget) -> None:
        window_width, window_height = 1024, 768
        window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Training Mode: Da Vinci Surgical Simulator")

        status_text = ""
        current_tool = "scalpel"
        is_operating = False
        level = 1  # 1: Easy, 2: Medium, 3: Hard

        health_bar_width = 200
        health_bar_height = 30

        cursor_pos = (0, 0)

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_tool = "scalpel"
                    elif event.key == pygame.K_2:
                        current_tool = "forceps"
                    elif event.key == pygame.K_3:
                        current_tool = "suture"
                    elif event.key == pygame.K_4:
                        current_tool = "laser"
                    elif event.key == pygame.K_5:
                        current_tool = "electrocautery"
                    elif event.key == pygame.K_6:
                        current_tool = "harmonic_scalpel"
                    elif event.key == pygame.K_l:  # Switch level
                        level = (level % 3) + 1
                    elif event.key == pygame.K_SPACE:
                        is_operating = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        is_operating = False

            if is_operating:
                result = self.operate(target, current_tool)
                status_text = f"{result.get_message()}\nHealth: {target.get_health()}"

                if level == 2:
                    target.set_health(target.get_health() - 2)
                elif level == 3:
                    target.set_health(target.get_health() - 3)

            cursor_pos = pygame.mouse.get_pos()

            # Drawing
            window.fill((50, 50, 50))

            # Health bar
            health_bar_width_current = max(
                0, min(health_bar_width, target.get_health() * 2)
            )
            pygame.draw.rect(
                window,
                (0, 255, 0),
                (20, 70, health_bar_width_current, health_bar_height),
            )

            # Operation area with different colors based on level
            operation_area_color = {
                1: (0, 255, 0),  # Green for Easy
                2: (255, 255, 0),  # Yellow for Medium
                3: (255, 0, 0),  # Red for Hard
            }[level]
            pygame.draw.circle(window, operation_area_color, (424, 350), 150)

            # Render status text
            status_surface = self.font.render(status_text, True, (255, 255, 255))
            window.blit(status_surface, (20, 20))

            # Render level text
            level_text = (
                f"Level: {'Easy' if level == 1 else 'Medium' if level == 2 else 'Hard'}"
            )
            level_surface = self.font.render(level_text, True, (255, 255, 0))
            window.blit(level_surface, (20, 120))

            # Render cursor
            pygame.draw.circle(window, (255, 255, 255), cursor_pos, 10)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def get_operation_data(self, target: OperationTarget) -> Dict[str, Any]:
        return {"targetName": target.get_name(), "finalHealth": target.get_health()}

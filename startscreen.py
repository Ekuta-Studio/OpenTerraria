import pygame
from global_settings import *

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(default_font, 36)

    def display(self):
        self.screen.fill((123, 104, 238))  # Sky color
        lines = [
            "Terraria"
        ]
        y = 100
        for line in lines:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (100, y))
            y += 50
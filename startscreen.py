import pygame
from global_settings import *
from block import Block  # Import the Block class to create blocks

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = 800
        self.screen_height = 600
        self.title_font = pygame.font.Font(default_font, 39)
        self.font = pygame.font.Font(default_font, 16)
        self.title = pygame.image.load("images/gui/title.png")
        
        # Initialize block textures
        self.block_images = {
            "grass": pygame.image.load("images/blocks/grass.png"),
            "dirt": pygame.image.load("images/blocks/dirt.png"),
            "stone": pygame.image.load("images/blocks/stone.png")
        }
        self.block_size = 15  # Size of each block
        for key in self.block_images:
            self.block_images[key] = pygame.transform.scale(self.block_images[key], (self.block_size, self.block_size))
        
        # Generate terrain blocks
        self.blocks = self.generate_terrain()

    def generate_terrain(self):
        """
        Generate terrain blocks for the start screen.
        """
        blocks = []
        ground_level = self.screen_height - self.block_size  # Ground level at the bottom of the screen
        
        # Generate a simple flat terrain
        for x in range(0, self.screen_width, self.block_size):
            # Top layer is grass
            blocks.append(Block(x, ground_level - self.block_size, "grass", self.block_size, self.block_images))
            # Next few layers are dirt
            for y in range(ground_level, ground_level + 3 * self.block_size, self.block_size):
                blocks.append(Block(x, y, "dirt", self.block_size, self.block_images))
            # Everything below is stone
            for y in range(ground_level + 3 * self.block_size, self.screen_height, self.block_size):
                blocks.append(Block(x, y, "stone", self.block_size, self.block_images))
        
        return blocks

    def display(self):
        """
        Display the start screen with the background, terrain, and text.
        """
        # Fill the screen with sky color
        self.screen.fill((123, 104, 238))  # Sky color
        
        # Draw the terrain blocks
        for block in self.blocks:
            block.draw(self.screen, 0, 0)  # Draw blocks without camera offset
        
        # Draw the key guide lines
        lines = [
            'Key guide:',
            'W S A D:Move',
            '"Ctrl + -" or "Ctrl + =":Change zoom',
            'Space:Jump',
            'Esc:Pause',
            'Left mouse:Destory block',
            'Right mouse:Place block',
            'Scroll or g/h:Switch block',
            'L:Add health',
            '',
            'Terraria by Re-Logic',
            'OpenTerraria by Ekuta Studio'
        ]
        y = 200
        title_rect = self.title.get_rect()
        title_rect.center = self.screen_width // 2, self.screen_height // 2 - 195
        self.screen.blit(self.title, title_rect)
        startgame_tips = self.font.render('(Create/Load world also start game.)', True, (255, 255, 255))
        self.screen.blit(startgame_tips,(self.screen_width // 2 - 139, self.screen_height // 2 + 195))
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (100, y))
            y += 17
import pygame

class Block:
    def __init__(self, x, y, block_type, block_size, block_images):
        self.rect = pygame.Rect(x, y, block_size, block_size)
        self.type = block_type
        self.image = block_images[block_type]
        self.x = x
        self.y = y
        self.block_type = block_type
        self.size = block_size
        self.blocks_player = block_type != "wood_wall"

    def draw(self, screen, camera_x, camera_y):
        """
        Draw the block
        :param screen: Pygame screen object
        :param camera_x: Camera x offset
        :param camera_y: Camera y offset
        """
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
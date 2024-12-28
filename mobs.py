import pygame
import random

class Slime:
    def __init__(self, x, y, image_path, block_size):
        """
        Initialize a Slime mob.
        :param x: Initial x-coordinate of the slime.
        :param y: Initial y-coordinate of the slime.
        :param image_path: Path to the slime's texture.
        :param block_size: Size of a block (used to scale the slime's texture).
        """
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (block_size, block_size))
        self.rect = pygame.Rect(x, y, block_size, block_size)
        self.speed = -80  # Slowest speed
        self.direction = 1  # 1 for right, -1 for left
        self.gravity = 1
        self.velocity_y = 0
        self.jump_power = 10
        self.on_ground = False
        self.health = 3  # Slimes have health

    def update(self, blocks):
        """
        Update the slime's position and state.
        :param blocks: List of blocks in the game for collision detection.
        """
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.rect.y = self.y

        # Check for collisions with blocks
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.velocity_y > 0:  # Colliding from above
                    self.y = block.rect.top - self.rect.height
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Colliding from below
                    self.y = block.rect.bottom
                    self.velocity_y = 0

        # Move horizontally
        self.x += self.speed * self.direction
        self.rect.x = self.x

        # Check for collisions with blocks horizontally
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.direction == 1:
                    self.x = block.rect.left - self.rect.width
                else:
                    self.x = block.rect.right
                self.direction *= -0.1  # Reverse direction

        # Jump randomly
        if self.on_ground and random.randint(0, 100) < 5:  # 5% chance to jump
            self.velocity_y = -self.jump_power

    def draw(self, screen, camera_x, camera_y):
        """
        Draw the slime on the screen.
        :param screen: The game screen.
        :param camera_x: Camera's x offset.
        :param camera_y: Camera's y offset.
        """
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))

    def take_damage(self, damage):
        """
        Reduce the slime's health when attacked.
        :param damage: Amount of damage to deal.
        """
        self.health -= damage
        if self.health <= 0:
            return True  # Slime is dead
        return False
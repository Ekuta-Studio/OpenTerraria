import pygame
import sys
import json
from block import Block
from global_settings import *
from mobs import Slime
import random
from perlin_noise import *
import os

class Game:
    def __init__(self, screen):
        self.skin_left = self.get_skin('skin.tr',1)
        self.skin_right = self.get_skin('skin.tr',2)
        self.screen = screen
        self.screen_width = 800
        self.screen_height = 600
        self.block_size = 15

        # World generation parameters
        self.world_width = 256  # Number of blocks in the world width
        self.world_height = 10  # Number of blocks in the world height
        self.seed = random.randint(0, 1000)  # Random seed for world generation
        self.scale = 24.0  # Scale of the noise
        self.perlin = PerlinNoise1D(self.seed)  # Initialize Perlin noise generator

        # Load player textures
        self.player_image_right = pygame.image.load(self.skin_right)
        self.player_image_right = pygame.transform.scale(self.player_image_right, (30, 46))
        self.player_image_left = pygame.image.load(self.skin_left)
        self.player_image_left = pygame.transform.scale(self.player_image_left, (30, 46))

        # Set initial player image
        self.player_image = self.player_image_left

        # Load block textures
        self.block_images = {
            "grass": pygame.image.load("images/blocks/grass.png"),
            "dirt": pygame.image.load("images/blocks/dirt.png"),
            "stone": pygame.image.load("images/blocks/stone.png"),
            "wood_wall": pygame.image.load("images/blocks/wood_wall.png")
        }
        for key in self.block_images:
            self.block_images[key] = pygame.transform.scale(self.block_images[key], (self.block_size, self.block_size))

        # Initialize player
        self.player_x = self.screen_width // 2 - 15  # Center horizontally
        self.player_y = self.screen_height - 43 - self.block_size  # Initial player position
        self.player_speed = 5
        self.player_jump_power = 15
        self.player_gravity = 1
        self.player_velocity_y = 0
        self.player_jumpback = 0
        self.player_jumping = 0
        self.fall_height = 0

        # Initialize blocks
        self.blocks = []
        self.generate_world()

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # Current block type
        self.block_types = ["grass", "dirt", "stone", "wood_wall"]
        self.current_block_type_index = 0
        self.current_block_type = self.block_types[self.current_block_type_index]

        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0

        # Touch mode button
        self.touch_button_image = pygame.image.load("images/gui/touch_button.png")
        self.touch_button_image = pygame.transform.scale(self.touch_button_image, (60, 60))  # Adjust button size
        self.touch_button_rect = self.touch_button_image.get_rect(topright=(self.screen_width - 10, 10))

        # Touch UI images
        self.touch_ui_images = {
            "up": pygame.image.load("images/gui/touch_move_up.png"),
            "down": pygame.image.load("images/gui/touch_move_down.png"),
            "left": pygame.image.load("images/gui/touch_move_left.png"),
            "right": pygame.image.load("images/gui/touch_move_right.png")
        }

        # Touch UI scale
        for direction in self.touch_ui_images:
            self.touch_ui_images[direction] = pygame.transform.scale(self.touch_ui_images[direction], (80, 80))

        # Touch UI positions
        self.touch_ui_rects = {
            "up": self.touch_ui_images["up"].get_rect(bottomleft=(50, self.screen_height - 150)),
            "down": self.touch_ui_images["down"].get_rect(topleft=(50, self.screen_height - 100)),
            "left": self.touch_ui_images["left"].get_rect(topright=(250, self.screen_height - 100)),
            "right": self.touch_ui_images["right"].get_rect(topleft=(300, self.screen_height - 100))
        }

        # Touch mode flag
        self.touch_mode = False
        self.touch_button_pressed = False  # Touch button state

        # Health system
        self.health = 100  # Initial health
        self.max_health = 100  # Maximum health
        self.death_height = 25 * self.block_size  # Death height
        self.spawn_point = (self.player_x, self.player_y)  # Spawn point
        self.fall_height = 0

        # Load slime texture path
        self.slime_image_path = "images/mobs/slime.png"
        self.slimes = []  # List to store active slimes

        # Slime spawn timer
        self.slime_spawn_timer = 0
        self.slime_spawn_interval = 5000  # Spawn a slime every 5 seconds

        # Attack variables
        self.attack_cooldown = 0
        self.attack_duration = 10  # Duration of the attack animation
        self.attack_range = 50  # Range of the attack
        self.attack_damage = 1  # Damage per attack

    def generate_world(self):
        """Generate the world using 1D Perlin noise."""
        for x in range(self.world_width):
            # Generate Perlin noise value (range: -1 to 1)
            noise_value = self.perlin.noise(x / self.scale)
            
            # Map noise value to terrain height (range: 10 to 30 blocks)
            terrain_height = int((noise_value + 1) * 10 + 10)  # Adjust range as needed

            # Calculate the ground level (bottom of the screen)
            ground_level = self.screen_height - self.block_size

            # Generate blocks from ground level upwards
            for y in range(ground_level - terrain_height * self.block_size, ground_level, self.block_size):
                if y == ground_level - self.block_size:
                    block_type = "stone"  # Top layer is grass
                elif y >= ground_level - 10 * self.block_size:
                    block_type = "dirt"  # Next few layers are dirt
                else:
                    block_type = "grass"  # Everything below is stone

                # Add block to the world
                self.blocks.append(Block(x * self.block_size, y, block_type, self.block_size, self.block_images))

    def run(self, events):
        self.handle_events(events)
        self.update_player()
        self.update_slimes()  # Update slimes
        self.update_attack()  # Update attack cooldown
        self.draw_game()
        self.clock.tick(60)  # Increase frame rate to 60 FPS for smoother movement

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
                # Check if the touch button is clicked
                if self.touch_button_rect.collidepoint(event.pos):
                    self.touch_mode = not self.touch_mode  # Toggle touch mode
            if event.type == pygame.MOUSEWHEEL:  # Handle mouse wheel scroll
                self.handle_mouse_wheel(event)

        # Handle touch UI clicks
        if self.touch_mode:
            mouse_pos = pygame.mouse.get_pos()
            for direction, rect in self.touch_ui_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.handle_touch_ui_click(direction)

        # Handle key events
        keys = pygame.key.get_pressed()
        if keys[pygame.K_g]:  # Press 'g' to switch to the previous block type
            self.switch_block_type(-1)
        if keys[pygame.K_h]:  # Press 'h' to switch to the next block type
            self.switch_block_type(1)
        if keys[pygame.K_LCTRL] and keys[pygame.K_EQUALS]:  # Ctrl+= to zoom in
            self.camera_zoom += 0.1
        if keys[pygame.K_LCTRL] and keys[pygame.K_MINUS]:  # Ctrl+- to zoom out
            self.camera_zoom -= 0.1
            if self.camera_zoom < 0.5:
                self.camera_zoom = 0.5
        if keys[pygame.K_k]:  # Press 'k' to attack
            self.attack()

    def handle_mouse_click(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Adjust mouse position based on zoom and camera offset
        mouse_x = int((mouse_x - (self.screen_width - self.screen_width * self.camera_zoom) // 2) / self.camera_zoom) + self.camera_x
        mouse_y = int((mouse_y - (self.screen_height - self.screen_height * self.camera_zoom) // 2) / self.camera_zoom) + self.camera_y

        # Check if the mouse is within the 5-block range around the player
        if abs(mouse_x - self.player_x) > 10 * self.block_size or abs(mouse_y - self.player_y) > 10 * self.block_size:
            return  # Ignore clicks outside the range

        if event.button == 1:  # Left click: Place block
            block_x = (mouse_x // self.block_size) * self.block_size
            block_y = (mouse_y // self.block_size) * self.block_size
            if not any(block.rect.collidepoint(block_x, block_y) for block in self.blocks):
                self.blocks.append(Block(block_x, block_y, self.current_block_type, self.block_size, self.block_images))
        elif event.button == 3:  # Right click: Remove block
            for block in self.blocks:
                if block.rect.collidepoint(mouse_x, mouse_y):
                    self.blocks.remove(block)

    def handle_mouse_wheel(self, event):
        """Handle mouse wheel scroll to switch block types."""
        if event.y > 0:  # Scroll up
            self.switch_block_type(-1)
        elif event.y < 0:  # Scroll down
            self.switch_block_type(1)

    def switch_block_type(self, direction):
        """Switch the current block type based on the direction (1 for next, -1 for previous)."""
        self.current_block_type_index += direction
        if self.current_block_type_index >= len(self.block_types):
            self.current_block_type_index = 0
        elif self.current_block_type_index < 0:
            self.current_block_type_index = len(self.block_types) - 1
        self.current_block_type = self.block_types[self.current_block_type_index]

    def handle_touch_ui_click(self, direction):
        if direction == "up":
            if self.player_velocity_y == 0:  # Jump
                self.player_velocity_y = -self.player_jump_power
        elif direction == "down":
            pass  # No action for down
        elif direction == "left":
            self.player_x -= self.player_speed
            self.player_image = self.player_image_left  # Set image to left when moving left
        elif direction == "right":
            self.player_x += self.player_speed
            self.player_image = self.player_image_right  # Set image to right when moving right

    def update_slimes(self):
        """
        Update all slimes in the game.
        """
        # Update slime positions
        for slime in self.slimes:
            slime.update(self.blocks)

        # Remove slimes that are off-screen
        self.slimes = [slime for slime in self.slimes if slime.x > -100 and slime.x < self.screen_width + 100]

        # Spawn new slimes
        current_time = pygame.time.get_ticks()
        if current_time - self.slime_spawn_timer > self.slime_spawn_interval:
            self.spawn_slime()
            self.slime_spawn_timer = current_time

    def spawn_slime(self):
        """
        Spawn a slime at a random position near the player, ensuring it's on the ground.
        """
        spawn_x = self.player_x + random.randint(-200, 200)
        spawn_y = self.player_y  # Spawn at ground level

        # Adjust spawn_y to ensure the slime is on the ground
        for block in self.blocks:
            if block.rect.collidepoint(spawn_x, spawn_y):
                spawn_y = self.player_y  # Place slime on top of the block
                Slime(spawn_x,spawn_y,self.slime_image_path,15)
                break

        

        # Check if the spawn position overlaps with existing slimes
        slime_rect = pygame.Rect(spawn_x, spawn_y, 25, 25)
        for slime in self.slimes:
            if slime_rect.colliderect(slime.rect):
                return  # Skip spawning if overlapping

        slime = Slime(spawn_x, spawn_y, self.slime_image_path, 25)
        self.slimes.append(slime)

    def attack(self):
        """
        Handle player attacks.
        """
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_duration

            # Define the attack area based on player direction
            if self.player_image == self.player_image_left:
                attack_rect = pygame.Rect(self.player_x - self.attack_range, self.player_y, self.attack_range, 46)
            else:
                attack_rect = pygame.Rect(self.player_x + 29, self.player_y, self.attack_range, 46)

            # Check for collisions with slimes
            for slime in self.slimes[:]:
                if attack_rect.colliderect(slime.rect):
                    if slime.take_damage(self.attack_damage):
                        self.slimes.remove(slime)  # Remove slime if it dies

    def update_attack(self):
        """
        Update the attack cooldown.
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def update_player(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.player_x -= self.player_speed
            self.player_image = self.player_image_left  # Set image to left when moving left
        if keys[pygame.K_d]:
            self.player_x += self.player_speed
            self.player_image = self.player_image_right  # Set image to right when moving right
        if keys[pygame.K_SPACE] and self.player_velocity_y == 0 and self.player_jumping == 0:  # Jump
            self.player_velocity_y = -self.player_jump_power
            self.player_jumpback = self.player_y  # Record the jump start position
            self.player_jumping = 1  # Set jumping state to 1

        # Add gravity
        if self.player_velocity_y < 10:
            self.player_velocity_y += self.player_gravity

        # Update player Y position
        self.player_y += self.player_velocity_y

        # Handle collisions
        self.handle_player_collisions()

        # Prevent player from falling out of the screen
        if self.player_y + 46 > self.screen_height:
            self.player_y = self.screen_height - 46
            self.player_velocity_y = 0

        # Check for fall damage when player lands
        if self.player_velocity_y == 0 and self.player_jumping == 1:  # Player has landed
            fall_height = (self.player_y - self.player_jumpback) / self.block_size  # Calculate fall height in blocks
            if fall_height > 25:  # If fall height is greater than 25 blocks
                self.health -= 10  # Subtract 10 health
                if self.health <= 0:  # Check if health is 0 or below
                    self.die()  # Call die method if health is 0 or below
            self.player_jumping = 0  # Reset jumping state

        # Update camera position to keep the player centered
        self.camera_x = self.player_x - self.screen_width // 2
        self.camera_y = self.player_y - self.screen_height // 2

    def handle_player_collisions(self):
        player_rect = pygame.Rect(self.player_x, self.player_y, 30, 46)
        for block in self.blocks:
            if block.blocks_player and player_rect.colliderect(block.rect):
                if self.player_velocity_y > 0:  # Colliding from above
                    self.player_y = block.rect.top - 46
                    self.player_velocity_y = 0
                elif self.player_velocity_y < 0:  # Colliding from below
                    self.player_y = block.rect.bottom
                    self.player_velocity_y = 0

        # Check collisions with slimes
        for slime in self.slimes:
            if player_rect.colliderect(slime.rect):
                self.health -= 6  # Reduce health by 6
                if self.health <= 0:
                    self.die()

    def die(self):
        self.player_x, self.player_y = self.spawn_point
        self.player_velocity_y = 0
        self.health = self.max_health
        self.spawn_point = (self.player_x, self.player_y)  # Update spawn point
        pygame.time.delay(5000)  # Respawn after 5 seconds

    def draw_game(self):
        # Create a temporary surface to draw the game elements
        temp_surface = pygame.Surface((self.screen_width, self.screen_height))
        temp_surface.fill((123, 104, 238))  # Fill with sky color

        # Draw blocks on the temporary surface
        for block in self.blocks:
            block.draw(temp_surface, self.camera_x, self.camera_y)

        # Draw Slime mobs
        for slime in self.slimes:
            slime.draw(temp_surface, self.camera_x, self.camera_y)

        # Draw the player last to ensure it's on top
        temp_surface.blit(self.player_image, (self.player_x - self.camera_x, self.player_y - self.camera_y))

        # Scale the temporary surface to the desired zoom level
        scaled_surface = pygame.transform.scale(temp_surface, 
                                                (int(self.screen_width * self.camera_zoom), 
                                                int(self.screen_height * self.camera_zoom)))

        # Calculate the offset to keep the player centered
        offset_x = (self.screen_width - scaled_surface.get_width()) // 2
        offset_y = (self.screen_height - scaled_surface.get_height()) // 2

        # Blit the scaled surface onto the main screen with the offset
        self.screen.blit(scaled_surface, (offset_x, offset_y))

        # Draw the current block type on the screen
        font = pygame.font.Font(default_font, 16)
        block_type_text = f"Current Block: {self.current_block_type.capitalize()}"
        text_surface = font.render(block_type_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, self.screen_height - 30))

        # Draw health bar
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 10
        pygame.draw.rect(self.screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (health_bar_x, health_bar_y, int(health_bar_width * (self.health / self.max_health)), health_bar_height))

        # Draw touch mode button
        self.screen.blit(self.touch_button_image, self.touch_button_rect)

        # Draw touch UI
        if self.touch_mode:
            for direction, rect in self.touch_ui_rects.items():
                self.screen.blit(self.touch_ui_images[direction], rect)

    def save_game(self, filename="save.json"):
        save_data = {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "blocks": [(block.x, block.y, block.block_type) for block in self.blocks],
            "health": self.health,
            "spawn_point": self.spawn_point
        }
        with open(filename, "w") as file:
            json.dump(save_data, file)

    def load_game(self, filename="save.json"):
        try:
            with open(filename, "r") as file:
                save_data = json.load(file)
                self.player_x = save_data["player_x"]
                self.player_y = save_data["player_y"]
                self.blocks = [Block(x, y, block_type, self.block_size, self.block_images) for x, y, block_type in save_data["blocks"]]
                self.health = save_data["health"]
                self.spawn_point = save_data["spawn_point"]
        except FileNotFoundError:
            print("Save file not found.")

    def get_skin(self, filename, line_number): # Get Config
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                file.write("images/player.png\n")
                file.write("images/player-to-right.png")
        with open(filename, 'r') as file:
            for current_line_number, line in enumerate(file, 1):
                if current_line_number == line_number:
                    return line.strip()
            return None
        

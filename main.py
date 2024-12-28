import pygame
import sys
from game import Game
from startscreen import StartScreen
from global_settings import *
import time

# Initialize Pygame
pygame.init()

# Set screen size
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Terraria")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Main loop
def main():
    game = Game(screen)
    startscreen = StartScreen(screen)
    show_startscreen = True  # Start with the guide
    pygame.mixer.music.load('sounds/music/title_screen.ogg')
    pygame.mixer.music.play(-1)
    font = pygame.font.Font(default_font, 36)

    # Load the start game button image
    start_game_button_image = pygame.image.load("images/gui/startgame_button.png")
    start_game_button_image = pygame.transform.scale(start_game_button_image, (50, 50))
    start_game_button_rect = start_game_button_image.get_rect(center=(screen_width // 2, screen_height // 2 + 170))

    # Load the startup image
    startup_image = pygame.image.load("images/gui/startup.png")
    startup_image = pygame.transform.scale(startup_image, (screen_width, screen_height))
    startup_alpha = 255  # Start with full opacity
    fade_speed = 5  # Speed of the fade effect

    clock = pygame.time.Clock()  # Create a clock object to control the frame rate

    paused = False
    pause_text = font.render("Paused", True, BLACK)
    pause_text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))

    # Pause menu buttons
    save_button_text = font.render("Save Game", True, BLACK)
    save_button_rect = save_button_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

    load_button_text = font.render("Load Game", True, BLACK)
    load_button_rect = load_button_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))

    # Start with the startup screen
    show_startup = True

    while True:
        # Handle events for the start screen or the game
        events = pygame.event.get()  # Get all events at once
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if show_startup:
            # Fade out the startup image
            if startup_alpha > 0:
                startup_alpha -= 2.5
                if startup_alpha < 0:
                    startup_alpha = 0
                startup_image.set_alpha(startup_alpha)
                screen.blit(startup_image, (0, 0))
            else:
                show_startup = False
        elif show_startscreen:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Press Enter to start the game
                        show_startscreen = False
                        pygame.mixer.music.load('sounds/music/overworld_day.ogg')
                        pygame.mixer.music.play(-1)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the start game button is clicked
                    if start_game_button_rect.collidepoint(event.pos):
                        show_startscreen = False
                        pygame.mixer.music.load('sounds/music/overworld_day.ogg')
                        pygame.mixer.music.play(-1)

            # Display the start screen
            startscreen.display()

            # Draw the start game button
            screen.blit(start_game_button_image, start_game_button_rect)
        elif paused:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Pressed ESC Paused
                        paused = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if save_button_rect.collidepoint(event.pos):
                        game.save_game()
                        print("Game saved!")
                    if load_button_rect.collidepoint(event.pos):
                        game.load_game()
                        print("Game loaded!")

            screen.fill(WHITE)
            screen.blit(pause_text, pause_text_rect)
            screen.blit(save_button_text, save_button_rect)
            screen.blit(load_button_text, load_button_rect)
        else:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True

            game.run(events)  # Pass events to the game

        # Display FPS on the screen
        fps = clock.get_fps()
        fps_text = f"FPS: {fps:.2f}"
        font = pygame.font.Font(default_font, 16)
        fps_surface = font.render(fps_text, True, BLACK)
        screen.blit(fps_surface, (10, 45))

        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

if __name__ == "__main__":
    main()
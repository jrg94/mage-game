# Simple pygame program

# Import and initialize the pygame library
import pygame
import random
from math import atan2, sin, cos

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    MOUSEBUTTONUP
)

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define a Player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        
    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
            
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
            
class Fireball(pygame.sprite.Sprite):
    """
    :param position: the position of the fireball
    :param target: tuple of (x, y) coordinates indicating the target location
    :param modifiers: a dictionary of modifiers to apply to the fireball
    """
    
    def __init__(self, position: pygame.Rect, target: tuple, modifiers: dict = {}):
        super(Fireball, self).__init__()
        
        # Initialize the surface
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        
        # Set required attributes
        self.rect = self.surf.get_rect(center=position.center)
        self.target = target
        
        # Set optional attributes
        self.speed = modifiers.get('speed', 10)
        self.radius = modifiers.get('radius', 5)
        
        # Compute attributes
        self.trajectory = self.calc_trajectory()
        
        # Draw the fireball
        pygame.draw.circle(
            self.surf, 
            (255, 0, 0), 
            self.surf.get_rect().center, 
            self.radius
        )
        
    def calc_trajectory(self):
        dx = self.target[0] - self.rect.centerx
        dy = self.target[1] - self.rect.centery
        radians = atan2(dy, dx)
        velocityx = self.speed * cos(radians)
        velocityy = self.speed * sin(radians)
        return velocityx, velocityy
    
    def update(self):
        self.rect.move_ip(*self.trajectory)
        if self.rect.right < 0:
            self.kill()
        
# Initialize pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Set up the drawing window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Instantiate player. Right now, this is just a rectangle.
player = Player()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
attacks = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Variable to keep the main loop running
running = True

# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
        
        if event.type == MOUSEBUTTONUP and event.button == 1:
            fireball = Fireball(player.rect.copy(), pygame.mouse.get_pos())
            all_sprites.add(fireball)
            attacks.add(fireball)

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False
            
    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()
    
    # Update the player sprite based on user keypresses
    player.update(pressed_keys)
    
    # Update fireball position
    attacks.update()
    
    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Update the display
    pygame.display.flip()
    
    # Ensure program maintains a rate of 30 frames per second
    clock.tick(30)

# Done! Time to quit.
pygame.quit()

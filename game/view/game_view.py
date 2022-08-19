import controller.game_controller as game_controller
import pygame

import view.sprites as sprites


class GameView():
    """
    The game window as drawn on the screen.
    
    :param screen_width: the width of the screen in pixels.
    :param screen_height: the height of the screen in pixels.
    """
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        pygame.init()
        
        # Save user inputs
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Setup key fields
        self.controller = None
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((
            self.screen_width, 
            self.screen_height
        ))
        self.fps = 30
        
        # Initialize sprites and sprite groups
        self.player = sprites.Player()
        self.palette = sprites.Palette()
        self.attacks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.palette)
        
    def register_observer(self, controller: game_controller.GameController):
        """
        Sets up the controller to be notified of events.
        """
        self.controller = controller
        
    def create_projectile(self, modifiers: dict):
        """
        A method for generating a projectile sprite. 
        
        :param modifiers: a dictionary of modifiers for the projectile.
        """
        print(modifiers)
        projectile = sprites.Projectile()
        
        # Set starting position
        rect = projectile.surf.get_rect(center=self.player.rect.center)
        projectile.rect = rect
        
        # Set optional attributes
        radius = modifiers.get('radius_in_pixels', 5)
        color = modifiers.get('color_in_rgb', (255, 0, 0))

        # Draw projectile
        pygame.draw.circle(
            projectile.surf,
            color,
            projectile.surf.get_rect().center,
            radius
        )
        
        # Add projectile to sprite group
        self.attacks.add(projectile)
        self.all_sprites.add(projectile)

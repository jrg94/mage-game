import math

import pygame
from pygame.locals import RLEACCEL

import model
from eventmanager import *


class GraphicalView(object):
    """
    Draws the model state onto the screen.
    """

    def __init__(self, evManager: model.EventManager, model: model.GameEngine):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.

        Attributes:
        isinitialized (bool): pygame is ready to draw.
        screen (pygame.Surface): the screen surface.
        clock (pygame.time.Clock): keeps the fps constant.
        smallfont (pygame.Font): a small font.
        """

        self.evManager = evManager
        evManager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.fps = None
        self.meters_to_pixels = None
        self.screen = None
        self.clock = None
        self.smallfont = None
        self.player = None
        self.palette = None
        self.attacks = None
        self.all_sprites = None

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.rendermenu()
            if currentstate == model.STATE_PLAY:
                self.renderplay()
            if currentstate == model.STATE_HELP:
                self.renderhelp()
            self.clock.tick(self.fps)
        elif isinstance(event, InputEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_PLAY:
                if event.clickpos:
                    self.rendercast(event)
                if event.char and event.char in "1234":
                    self.renderpalette(event)

    def _compute_trajectory(self, speed: float, click_position: tuple) -> tuple:
        """
        A handy method for computing the path of a projectile in components
        of speed as pixels.

        :param speed: the speed of the projectile in meters per second.
        :return: the trajectory of the projectile in xy components of pixels/frame
        """
        dx = click_position[0] - self.player.rect.centerx
        dy = click_position[1] - self.player.rect.centery
        radians = math.atan2(dy, dx)
        velocityx = (speed * math.cos(radians) *
                     self.meters_to_pixels) / self.fps
        velocityy = (speed * math.sin(radians) *
                     self.meters_to_pixels) / self.fps
        return (velocityx, velocityy)

    def _create_projectile(self, modifiers: dict):
        """
        A method for generating a projectile sprite. 

        :param modifiers: a dictionary of modifiers for the projectile.
        """
        projectile = Projectile()

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

    def rendermenu(self):
        """
        Render the game menu.
        """
        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'You are in the Menu. Space to play. Esc exits.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def renderplay(self):
        """
        Render the game play.
        """

        self.screen.fill((0, 0, 0))
        self.model.palette.update_cooldowns(self.clock.get_time())
        self.all_sprites.update()
        somewords = self.smallfont.render(
            'You are playing the game. F1 for help.',
            True, 
            (0, 255, 0)
        )
        self.screen.blit(
            somewords, 
            (0, self.screen.get_height() - somewords.get_height())
        )
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def renderhelp(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'Help is here. space, escape or return.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def rendercast(self, event: InputEvent):
        """
        Render a spell cast.
        """
        
        if self.model.palette.can_cast_active_spell():
            
            # Reset projectile cooldown
            self.model.palette.reset_active_spell_cooldown()
            
            # Create projectile sprite
            active_palette_item = self.model.palette.get_active_item()
            trajectory = self._compute_trajectory(
                active_palette_item.get_spell().speed(), 
                event.clickpos
            )
            distance = math.ceil(
                active_palette_item.get_spell().distance() * self.meters_to_pixels
            )
            projectile = Projectile(
                trajectory,
                distance,
                self.player.rect.center,
            )

            # Set starting position
            rect = projectile.surf.get_rect(center=self.player.rect.center)
            projectile.rect = rect

            # Set optional attributes
            radius = math.ceil(
                active_palette_item.get_spell().radius() * self.meters_to_pixels)
            color = active_palette_item.get_spell().element().color

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

            # Render sprites
            self.all_sprites.update()
            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)
                
            pygame.display.flip()

    def renderpalette(self, event: InputEvent):
        """
        Render the palette.
        """
        self.screen.fill((0, 0, 0))
        self.model.palette.set_active_palette_item(int(event.char) - 1)
        self.all_sprites.update()
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Mage Game')
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.meters_to_pixels = self.screen.get_width() / self.model.world_width
        self.smallfont = pygame.font.Font(None, 40)
        self.player = Player(self.screen.get_rect().center)
        self.palette = Palette(self.model.palette)
        self.attacks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.palette)
        self.isinitialized = True


class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super(Player, self).__init__()
        self.surf = pygame.image.load("assets/player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=position)

    def update(self):
        pass


class Projectile(pygame.sprite.Sprite):
    """
    A generic projectile class that can be used to create different types of projectiles.
    """

    def __init__(self, trajectory: tuple, distance_in_pixels: int, pos: tuple):
        super(Projectile, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.trajectory = pygame.Vector2(trajectory)
        self.distance_in_pixels: int = distance_in_pixels
        self.travel_distance: float = 0

    def update(self):
        """
        Animates the projectile from a list of modifiers. 

        :param modifiers: a dictionary of modifiers for the projectile.
        """
        self.pos += self.trajectory
        self.travel_distance += math.sqrt(
            self.trajectory[0] * self.trajectory[0] + self.trajectory[1] * self.trajectory[1])
        self.rect.center = self.pos
        if self.rect.right < 0 or self.travel_distance >= self.distance_in_pixels:
            self.kill()


class Palette(pygame.sprite.Sprite):
    def __init__(self, palette: model.Palette):
        super(Palette, self).__init__()
        self.surf = pygame.Surface((200, 50))
        self.rect = self.surf.get_rect()
        self.palette: model.Palette = palette

    def update(self):
        left = 0
        for i, item in enumerate(self.palette.get_items()):
            if i == self.palette.get_active_item_index():
                pygame.draw.rect(
                    self.surf,
                    (0, 255, 0),
                    (left, 0, 50, 50),
                    width=2
                )
            else:
                pygame.draw.rect(
                    self.surf,
                    (255, 255, 255),
                    (left, 0, 50, 50),
                    width=2
                )
            pygame.draw.circle(
                self.surf,
                item.get_spell().element().color,
                (left + 25, 25),
                10
            )
            left += 50

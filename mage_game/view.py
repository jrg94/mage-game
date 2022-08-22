import math

import pygame
from pygame.locals import RLEACCEL

import model
from eventmanager import *


class GraphicalView(object):
    """
    Draws the model state onto the screen.
    
    :param event_manager: the event manager.
    :param model: the model.
    """

    def __init__(self, event_manager: model.EventManager, model: model.GameEngine):
        self.evManager = event_manager
        event_manager.RegisterListener(self)
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

    def notify(self, event: Event):
        """
        Receive events posted to the message queue. 
        
        :param event: the event.
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
                self.render_menu()
            if currentstate == model.STATE_PLAY:
                self.render_play()
            if currentstate == model.STATE_HELP:
                self.render_help()
            self.clock.tick(self.fps)
        elif isinstance(event, InputEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_PLAY:
                if event.click_pos and event.button == "left":
                    self.render_cast(event)
                if event.char and event.char in "1234":
                    self.render_palette(event)

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

    def render_menu(self):
        """
        Render the game menu.
        """
        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'You are in the Menu. Space to play. Esc exits.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def render_play(self):
        """
        Render the game play.
        """

        self.screen.fill((0, 0, 0))
        self.model.palette.update_cooldowns(self.clock.get_time())
        self.model.palette.update_casting_time(self.clock.get_time())
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

    def render_help(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'Help is here. space, escape or return.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def render_cast(self, event: InputEvent):
        """
        Render a spell cast.
        """
        
        if self.model.palette.can_cast_active_spell():
            
            self.model.palette.reset_casting_time()
        
            # Create projectile sprite
            active_spell = self.model.palette.get_active_item().get_spell()
            trajectory = self._compute_trajectory(
                active_spell.speed(),
                event.click_pos
            )
            distance = math.ceil(
                active_spell.distance() * self.meters_to_pixels
            )
            projectile = Projectile(
                trajectory,
                distance,
                self.player.rect.center,
                active_spell.cast_time()
            )

            # Set starting position
            rect = projectile.surf.get_rect(center=self.player.rect.center)
            projectile.rect = rect

            # Set optional attributes
            radius = math.ceil(
                active_spell.radius() * self.meters_to_pixels)
            color = active_spell.element().color

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

    def render_palette(self, event: InputEvent):
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
    """
    The player sprite class.
    
    :param position: the position of the player on the screen.
    """
    
    def __init__(self, position: tuple):
        super(Player, self).__init__()
        self.sprites = [pygame.image.load(f'assets/player{i}.png') for i in range(1, 3)]
        self.surf = self.sprites[0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=position)
        self.current_sprite = 0

    def update(self):
        self.current_sprite += .1
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.surf = self.sprites[int(self.current_sprite)]


class Projectile(pygame.sprite.Sprite):
    """
    A generic projectile sprite class that can be used to 
    create different types of projectiles.
    
    :param trajectory: the xy velocity of the projectile
    :param distance_in_pixels: the distance the projectile should travel in pixels
    :param pos: the starting position of the projectile.
    """

    def __init__(self, trajectory: tuple, distance_in_pixels: int, pos: tuple, cast_time: float):
        super(Projectile, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.trajectory = pygame.Vector2(trajectory)
        self.distance_in_pixels: int = distance_in_pixels
        self.cast_time = cast_time
        self.travel_distance: float = 0
        self.start_time: float = pygame.time.get_ticks()

    def update(self):
        """
        Animates the projectile. 
        """
        if pygame.time.get_ticks() - self.start_time > self.cast_time * 1000:
            self.pos += self.trajectory
            self.travel_distance += math.sqrt(self.trajectory[0] * self.trajectory[0] + self.trajectory[1] * self.trajectory[1])
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
        self.surf.fill((0, 0, 0))
        active_spell = self.palette.get_active_item().get_spell()
        for i, item in enumerate(self.palette.get_items()):
            # Draw green square for active item
            if i == self.palette.get_active_item_index():
                pygame.draw.rect(
                    self.surf,
                    (0, 255, 0),
                    (left, 0, 50, 50),
                    width=2
                )
            # Draw white square otherwise
            else:
                pygame.draw.rect(
                    self.surf,
                    (255, 255, 255),
                    (left, 0, 50, 50),
                    width=2
                )
            # Show cast time 
            if self.palette.get_remaining_casting_time() > 0:
                ratio = self.palette.get_remaining_casting_time() / (active_spell.cast_time() * 1000)
                pygame.draw.rect(
                    self.surf,
                    (155, 155, 155, 100),
                    (left + 2, 2, 46, 46 * ratio)
                )
            # Add colored circle to square
            pygame.draw.circle(
                self.surf,
                item.get_spell().element().color,
                (left + 25, 25),
                10
            )
            left += 50

            
        

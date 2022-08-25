import math

import pygame

from ..eventmanager import *
from ..model import *
from .sprites import *


class GraphicalView(object):
    """
    Draws the model state onto the screen.

    :param event_manager: the event manager.
    :param model: the model.
    """

    def __init__(self, event_manager: EventManager, model: GameEngine):
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
        self.enemies = None
        self.help = None

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
            if currentstate == GameState.STATE_MENU:
                self.render_menu()
            if currentstate == GameState.STATE_PLAY:
                self.render_play()
            if currentstate == GameState.STATE_HELP:
                self.render_help()
            self.clock.tick(self.fps)
        elif isinstance(event, InputEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == GameState.STATE_PLAY:
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

        # Process play game logic
        self.handle_collisions()
        self.model.character._palette.update_cooldowns(self.clock.get_time())
        self.model.character._palette.update_casting_time(self.clock.get_time())
        self.all_sprites.update()

        # Render the scene
        self.screen.fill((0, 0, 0))
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
        self.help.update()
        self.screen.blit(self.help.surf, self.help.rect)
        pygame.display.flip()

    def render_cast(self, event: InputEvent):
        """
        Render a spell cast.
        """
        if self.model.character.cast():

            # Create projectile sprite
            active_spell = self.model.character._palette.get_active_item().get_spell()
            radius = math.ceil(active_spell.get_attribute(
                SpellAttribute.RADIUS) * self.meters_to_pixels)
            color = active_spell.element().color
            trajectory = self._compute_trajectory(
                active_spell.get_attribute(SpellAttribute.SPEED),
                event.click_pos
            )
            projectile = ProjectileSprite(
                active_spell,
                trajectory,
                self.player.rect.center,
                self.meters_to_pixels
            )

            # Set starting position
            projectile.rect = projectile.surf.get_rect(
                center=self.player.rect.center)

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
        self.model.character._palette.set_active_palette_item(
            int(event.char) - 1)
        self.all_sprites.update()
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def handle_collisions(self):
        for attack in self.attacks:
            enemies: list[pygame.sprite.Sprite] = pygame.sprite.spritecollide(
                attack, self.enemies, False)
            for enemy in enemies:
                if enemy not in attack.hit:
                    damage: AttributeTracking = attack.source.get_tracking(
                        SpellAttribute.DAMAGE)
                    damage.trigger_event()
                    attack.hit.append(enemy)
                    enemy.hit(damage.effective_value())
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

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Setting up player
        self.player = PlayerSprite()
        self.player.rect = self.player.surf.get_rect(
            center=self.screen.get_rect().center)
        self.all_sprites.add(self.player)

        # Setting up palette
        self.palette = PaletteSprite(self.model.character._palette)
        self.all_sprites.add(self.palette)

        # Setting up dummy enemies
        for enemy in self.model.enemies:
            dummy = DummySprite(enemy)
            dummy.rect = dummy.surf.get_rect(center=(400, 400))
            self.enemies.add(dummy)
            self.all_sprites.add(dummy)

        # Setting up help screen
        self.help = ProgressSprite(self.model.character)
        self.help.rect = self.help.surf.get_rect(
            center=self.screen.get_rect().center)

        # Declaring the view initialized
        self.isinitialized = True

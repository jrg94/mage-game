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
        self.event_manager: EventManager = event_manager
        self.event_manager.RegisterListener(self)
        self.model: GameEngine = model
        
        # Graphics variables
        self.isinitialized: bool = False
        self.fps: int = None
        self.meters_to_pixels: float = None
        self.screen: pygame.Surface = None
        self.clock: pygame.time.Clock = None
        self.font: pygame.font.Font = None
        
        # Sprites
        self.player: PlayerSprite = None
        self.palette: PaletteSprite = None
        self.help: ProgressSprite = None
        
        # Sprite Groups
        self.attack_sprites: pygame.sprite.Group = None
        self.help_sprites: pygame.sprite.Group = None
        self.play_sprites: pygame.sprite.Group = None
        self.enemy_sprites: pygame.sprite.Group = None

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
            # TODO: add scroll wheel event to zoom in and out
            if currentstate == GameState.STATE_PLAY:
                if event.click_pos and event.button == "left":
                    self.render_cast(event)
                if event.char and event.char in "1234":
                    self.render_palette(event)

    def render_menu(self):
        """
        Render the game menu.
        """
        self.screen.fill((0, 0, 0))
        somewords = self.font.render(
            'You are in the Menu. Space to play. Esc exits.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def render_play(self):
        """
        Render the game play.
        """

        # Process play game logic
        self.handle_collisions() # TODO: where should this go?
        self.model.character._palette.update_cooldowns(self.clock.get_time())
        self.model.character._palette.update_casting_time(self.clock.get_time())

        # Render the scene
        self.screen.fill((0, 0, 0))
        self.play_sprites.update()
        self.play_sprites.draw(self.screen)
        pygame.display.flip()

    def render_help(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        self.help_sprites.update()
        self.help_sprites.draw(self.screen)
        pygame.display.flip()

    def render_cast(self, event: InputEvent):
        """
        Render a spell cast.
        
        :param event: the input event that triggered this cast
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
                self.player.rect.center,
                active_spell,
                trajectory,
                self.meters_to_pixels
            )

            # Set starting position
            projectile.rect = projectile.image.get_rect(
                center=self.player.rect.center)

            # Draw projectile
            pygame.draw.circle(
                projectile.image,
                color,
                projectile.image.get_rect().center,
                radius
            )

            # Add projectile to sprite group
            self.attack_sprites.add(projectile)
            self.play_sprites.add(projectile)

            # Render sprites
            self.play_sprites.update()
            self.play_sprites.draw(self.screen)

            pygame.display.flip()

    def render_palette(self, event: InputEvent):
        """
        Render the palette.
        
        :param event: the input event that triggered this change in palette.
        """
        self.screen.fill((0, 0, 0))
        self.model.character.select_palette_item(int(event.char) - 1)
        self.play_sprites.update()
        self.play_sprites.draw(self.screen)
        pygame.display.flip()

    def handle_collisions(self):
        """
        A helper method that detects when projectiles intersect
        with enemies. 
        """
        for attack in self.attack_sprites:
            enemies: list[pygame.sprite.Sprite] = pygame.sprite.spritecollide(
                attack, 
                self.enemy_sprites, 
                False
            )
            for enemy in enemies:
                if enemy not in attack.hit:
                    damage: AttributeTracking = attack.source.get_tracking(SpellAttribute.DAMAGE)
                    damage.trigger_event()
                    attack.hit.append(enemy)
                    enemy.hit(damage.effective_value())
        pygame.display.flip()
        
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
        velocityx = (speed * math.cos(radians) * self.meters_to_pixels) / self.fps
        velocityy = (speed * math.sin(radians) * self.meters_to_pixels) / self.fps
        return (velocityx, velocityy)

    def _init_misc_play_sprites(self) -> pygame.sprite.Group:
        """
        A helper method that initializes all of the sprites
        that are used during the play portion of the game.
        Not all play sprites are generated here.

        :return: a list of miscellaneous play sprites
        """
        
        group = pygame.sprite.Group()
        
        # Setting up player
        self.player = PlayerSprite(
            self.screen.get_rect().center, 
            self.model.character, 
            self.meters_to_pixels
        )
        group.add(self.player)
        
        # Setting up play text
        play_text = StateText(
            (0, self.screen.get_height() - self.font.get_height()),
            self.font,
            'You are playing the game. F1 for help.'
        )
        group.add(play_text)
        
        # Setting up palette
        self.palette = PaletteSprite((0, 0), self.model.character._palette)
        group.add(self.palette)
        
        return group
        
        
    def _init_enemy_sprites(self) -> pygame.sprite.Group:
        """
        A helper method for creating the initial enemies sprite group.

        :return: a list of enemy sprites
        """
        
        group = pygame.sprite.Group()

        # Setting up dummy enemies
        for enemy in self.model.enemies:
            dummy = DummySprite((400, 400), enemy)
            group.add(dummy)
            
        return group
    
    
    def _init_help_sprites(self) -> pygame.sprite.Group:
        """
        A helper method for creating all of the sprites
        seen in the help menu.

        :return: a group of help menu sprites
        """
        
        group = pygame.sprite.Group()
        
        # Setting up help screen
        self.help = ProgressSprite(
            self.screen.get_rect().center, 
            self.model.character
        )
        group.add(self.help)
        
        # Setting up help text
        help_text = StateText((0, 0), self.font, 'Help is here. space, escape or return.')
        group.add(help_text)
        
        return group
    
    
    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Mage Game')
        
        # Initialize graphics fields
        self.screen = pygame.display.set_mode((0, 0))
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.meters_to_pixels = self.screen.get_width() / self.model.character._view_width
        self.font = pygame.font.Font(None, 40)

        # Create sprite groups
        self.attack_sprites = pygame.sprite.Group()
        self.enemy_sprites = self._init_enemy_sprites()
        self.play_sprites = self._init_misc_play_sprites()
        self.play_sprites.add(*self.enemy_sprites.sprites())
        self.play_sprites.add(*self.attack_sprites.sprites())
        self.help_sprites = self._init_help_sprites()
        
        # Declaring the view initialized
        self.isinitialized = True

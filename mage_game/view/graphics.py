import math

import pygame

from mage_game.view.camera import CharacterCameraGroup

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
        
        # Play sprite groups
        self.attack_sprites: CharacterCameraGroup = None
        self.play_sprites: CharacterCameraGroup = None
        self.enemy_sprites: CharacterCameraGroup = None
        self.ui_sprites: pygame.sprite.Group = None
        
        # Menu sprite groups
        self.help_sprites: pygame.sprite.Group = None
        self.menu_sprites: pygame.sprite.Group = None
        
        # Actions keys
        self.palette_keys = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)
        self.movement_keys = (pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_w)
        self.cast_keys = (pygame.BUTTON_LEFT,)

    def notify(self, event: Event):
        """
        Receive events posted to the message queue. 

        :param event: the event.
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
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
        # TODO: keyboard and mouse events are two generic -> make them more specific like MoveEvent
        elif isinstance(event, KeyboardEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            # TODO: add scroll wheel event to zoom in and out
            if currentstate == GameState.STATE_PLAY:
                if event.key in self.palette_keys:
                    self.render_palette(event)
        elif isinstance(event, MouseEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == GameState.STATE_PLAY:
                if event.button in self.cast_keys:
                    self.render_cast()

    def render_menu(self):
        """
        Render the game menu.
        """
        self.screen.fill((0, 0, 0))
        self.menu_sprites.update()
        self.menu_sprites.draw(self.screen)
        pygame.display.flip()
        
    def render_help(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        self.help_sprites.update()
        self.help_sprites.draw(self.screen)
        pygame.display.flip()

    def render_play(self):
        """
        Render the game play.
        """

        # Process non-event based game logic
        self.handle_collisions()
        self.player.move(self.fps, self.meters_to_pixels)
        self.model.character._palette.update_cooldowns(self.clock.get_time())
        self.model.character._palette.update_casting_time(self.clock.get_time())

        # Render the scene
        self.screen.fill((0, 0, 0))
        self.play_sprites.update()
        self.play_sprites.camera_draw(self.player)
        self.ui_sprites.update()
        self.ui_sprites.draw(self.screen)
        pygame.display.flip()

    def render_cast(self):
        """
        Render a spell cast.
        
        :param event: the input event that triggered this cast
        """
        if self.model.character.cast():
            # Create a projectile and cast it
            source = self.model.character._palette.get_active_item().get_spell()
            projectile_speed = (source.get_attribute(SpellAttribute.SPEED) * self.meters_to_pixels) / self.fps 
            projectile_radius = source.get_attribute(SpellAttribute.RADIUS) * self.meters_to_pixels
            charge_frames = source.get_attribute(SpellAttribute.CAST_TIME) * self.fps
            cast_frames = (source.get_attribute(SpellAttribute.DISTANCE) / source.get_attribute(SpellAttribute.SPEED)) * self.fps
            diameter = math.ceil(projectile_radius * 2)
            projectile = ProjectileSprite(
                self.player,
                (diameter, diameter),
                source,
                self.play_sprites
            )
            projectile.cast(
                charge_frames,
                cast_frames,
                projectile_speed,
                projectile_radius
            )

            # Add projectile to sprite group
            self.attack_sprites.add(projectile)
            self.play_sprites.add(projectile)

            # Render sprites
            self.play_sprites.update()
            self.play_sprites.camera_draw(self.player)
            self.ui_sprites.update()
            self.ui_sprites.draw(self.screen)

            pygame.display.flip()

    def render_palette(self, event: KeyboardEvent):
        """
        Render the palette.
        
        :param event: the input event that triggered this change in palette.
        """
        self.screen.fill((0, 0, 0))
        self.model.character.select_palette_item(int(event.char) - 1)
        self.play_sprites.update()
        self.play_sprites.camera_draw(self.player)
        self.ui_sprites.update()
        self.ui_sprites.draw(self.screen)
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

    def _init_misc_play_sprites(self) -> CharacterCameraGroup:
        """
        A helper method that initializes all of the sprites
        that are used during the play portion of the game.
        Not all play sprites are generated here.

        :return: a list of miscellaneous play sprites
        """
        
        group = CharacterCameraGroup()
        
        # Setting up player
        self.player = PlayerSprite(
            self.screen.get_rect().center, 
            tuple(map(lambda x: x * self.meters_to_pixels, self.model.character._size)),
            self.model.character,
            group
        )
        group.add(self.player)
        
        return group
        
        
    def _init_enemy_sprites(self) -> CharacterCameraGroup:
        """
        A helper method for creating the initial enemies sprite group.

        :return: a list of enemy sprites
        """
        
        group = CharacterCameraGroup()

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
    
    def _init_menu_sprites(self) -> pygame.sprite.Group:
        """
        A helper methof for creating all the menu sprites.

        :return: a group of menu sprites
        """
        group = pygame.sprite.Group()
        
        menu_text = StateText(
            (self.screen.get_width() / 2, self.screen.get_height() / 2),
            self.font,
            'You are in the Menu. Space to play. Esc exits.',
            anchor="center"
        )
        group.add(menu_text)
        
        return group
    
    def _init_ui_sprites(self) -> pygame.sprite.Group:
        group = pygame.sprite.Group()
        
        # Setting up play text
        play_text = StateText(
            (0, self.screen.get_height() - self.font.get_height()),
            self.font,
            'You are playing the game. F1 for help.'
        )
        group.add(play_text)
        
        # Setting up palette
        self.palette = PaletteSprite(
            (10, 10), 
            (
                pygame.display.get_window_size()[0] / 8,
                pygame.display.get_window_size()[1] / 20
            ),
            self.model.character._palette
        )
        group.add(self.palette)
        
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
        self.attack_sprites = CharacterCameraGroup()
        self.enemy_sprites = self._init_enemy_sprites()
        self.play_sprites = self._init_misc_play_sprites()
        self.play_sprites.add(*self.enemy_sprites.sprites())
        self.play_sprites.add(*self.attack_sprites.sprites())
        self.ui_sprites = self._init_ui_sprites()
        self.help_sprites = self._init_help_sprites()
        self.menu_sprites = self._init_menu_sprites()
        
        # Declaring the view initialized
        self.isinitialized = True

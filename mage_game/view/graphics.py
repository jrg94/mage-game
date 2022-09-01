import math
import logging

import pygame

from mage_game.view.camera import CharacterCameraGroup

from ..eventmanager import *
from ..model import *
from .sprites import *

logger = logging.getLogger(__name__)


class GraphicalView(object):
    """
    Draws the model state onto the screen.

    :param event_manager: the event manager.
    :param model: the model.
    """

    def __init__(self, event_manager: EventManager, model: GameEngine) -> None:
        self.event_manager: EventManager = event_manager
        self.event_manager.register_listener(self)
        self.model: GameEngine = model
        
        # Graphics variables
        self.isinitialized: bool = False
        self.fps: int = None
        self.meters_to_pixels: float = None
        self.screen: pygame.Surface = None
        self.clock: pygame.time.Clock = None
        self.font: pygame.font.Font = None
        
        # Sprites
        self.new_game_button: ButtonSprite = None
        self.load_game_button: ButtonSprite = None
        self.player: PlayerSprite = None
        self.palette: PaletteSprite = None
        self.help: ProgressSprite = None
        
        # Play sprite groups
        self.attack_sprites: CharacterCameraGroup = None
        self.terrain_sprites: CharacterCameraGroup = None
        self.play_sprites: CharacterCameraGroup = None
        self.enemy_sprites: CharacterCameraGroup = None
        self.ui_sprites: pygame.sprite.Group = None
        self.title_screen_sprites: pygame.sprite.Group = None
        
        # Menu sprite groups
        self.help_sprites: pygame.sprite.Group = None
        self.menu_sprites: pygame.sprite.Group = None

    def notify(self, event: Event) -> None:
        """
        Receive events posted to the message queue. 

        :param event: the event.
        """
        if isinstance(event, InitializeEvent):
            self.initialize()
            return
        if self.isinitialized:
            if isinstance(event, QuitEvent):
                self._handle_quit_event()
            elif isinstance(event, TickEvent):
                self._handle_tick_event()
            elif isinstance(event, CastEvent):
                self._handle_cast_event()
            elif isinstance(event, PaletteSelectEvent):
                self._handle_palette_select_event(event)
            elif isinstance(event, MouseEvent):
                self._handle_mouse_event(event)
                
    def _handle_quit_event(self) -> None:
        """
        A helper method for processing quit events.
        """
        self.isinitialized = False
        pygame.quit()
    
    def _handle_tick_event(self) -> None:
        """
        A helper method for processing tick events.
        As the game is running, tick events will trigger
        different render methods.
        """
        current_state = self.model.state.peek()
        if current_state == GameState.STATE_INTRO:
            self.render_title_screen()
        if current_state == GameState.STATE_MENU:
            self.render_menu()
        if current_state == GameState.STATE_PLAY:
            self.render_play()
        if current_state == GameState.STATE_HELP:
            self.render_help()
        self.clock.tick()
        
    def _handle_cast_event(self) -> None:
        """
        A helper method for processing cast events.
        Cast events can be triggered in a variety of ways
        but should always result to a spell being cast, 
        if possible.
        """
        current_state = self.model.state.peek()
        if current_state == GameState.STATE_PLAY:
            self.trigger_cast_event()
            
    def _handle_palette_select_event(self, event: PaletteSelectEvent) -> None:
        """
        A helper method for processing palette select events.
        Palette select events are triggered when a user selects
        a spell using the proper key binding.

        :param event: the palette select event object
        """
        current_state = self.model.state.peek()
        if current_state == GameState.STATE_PLAY:
            self.trigger_palette_switch_event(event)
            
    def _handle_mouse_event(self, event: MouseEvent) -> None:
        """
        A helper method for processing mouse events.
        A mouse event occurs when the user presses 
        a mouse button. Right now, mouse events are 
        used to register button presses. More specific
        button press events should be crafted when
        possible.

        :param event: the mouse press event object
        """
        current_state = self.model.state.peek()
        if current_state == GameState.STATE_INTRO:
            self.trigger_menuing(event)

    def render_title_screen(self) -> None:
        """
        Renders the title screen.
        """
        
        logger.debug(
            f"Rendering the title screen with an FPS of {self.clock.get_fps()}." 
            f"The previous frame took {self.clock.get_time()} milliseconds."
        )
        self.screen.fill((0, 120, 80))
        game_name = self.font.render("Mage Game", True, (255, 255, 255))
        game_name_rect = game_name.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(game_name, game_name_rect)
        self.title_screen_sprites.update()
        self.title_screen_sprites.draw(self.screen)
        pygame.display.flip()

    def render_menu(self) -> None:
        """
        Render the game menu.
        """
        
        logger.debug(
            f"Rendering the game menu with an FPS of {self.clock.get_fps()}." 
            f"The previous frame took {self.clock.get_time()} milliseconds."
        )
        self.screen.fill((0, 0, 0))
        self.menu_sprites.update()
        self.menu_sprites.draw(self.screen)
        pygame.display.flip()
        
    def render_help(self) -> None:
        """
        Render the help screen.
        """

        logger.debug(
            f"Rendering the help menu with an FPS of {self.clock.get_fps()}." 
            f"The previous frame took {self.clock.get_time()} milliseconds."
        )
        self.screen.fill((0, 0, 0))
        self.help_sprites.update()
        self.help_sprites.draw(self.screen)
        pygame.display.flip()

    def render_play(self) -> None:
        """
        Render the game play.
        """

        logger.debug(
            f"Rendering the gameplay with an FPS of {self.clock.get_fps()}." 
            f"The previous frame took {self.clock.get_time()} milliseconds."
        )
        self.screen.fill((0, 0, 0))
        self.play_sprites.update()
        self.play_sprites.camera_draw(self.player)
        self.ui_sprites.update()
        self.ui_sprites.draw(self.screen)
        pygame.display.flip()

    def trigger_cast_event(self) -> None:
        """
        Creates a projectile to be rendered.
        
        :param event: the input event that triggered this cast
        """
        if self.model.character.cast():
            # Setup projectile variables
            source = self.model.character._palette.get_active_item().get_spell()
            projectile_radius = source.get_attribute(SpellAttribute.RADIUS) * self.meters_to_pixels
            diameter = math.ceil(projectile_radius * 2)
            
            # Create projectile
            projectile = ProjectileSprite(
                self.player,
                (diameter, diameter),
                source,
                self.play_sprites,
                self.enemy_sprites
            )
            
            # Cast projectile
            projectile.spawn(
                self.clock,
                self.meters_to_pixels
            )

            # Add projectile to sprite group
            self.attack_sprites.add(projectile)
            self.play_sprites.add(projectile)
            
    def trigger_menuing(self, event: MouseEvent):
        """
        A menuing method for the title screen.

        :param event: the mouse event object
        """
        
        if self.new_game_button.detect_press(event):
            self._new_game()
            self.event_manager.post(StateChangeEvent(GameState.STATE_PLAY))
        if self.load_game_button.detect_press(event):
            pass

    def trigger_palette_switch_event(self, event: PaletteSelectEvent):
        """
        Updates the palette to reflect the spell selection.
        
        :param event: the input event that triggered this change in palette.
        """
        
        self.model.character.select_palette_item(event.item)

    def _init_player_sprite(self) -> CharacterCameraGroup:
        """
        A helper method that initializes all of the sprites
        that are used during the play portion of the game.
        Not all play sprites are generated here.

        :return: a list of miscellaneous play sprites
        """
        
        group = CharacterCameraGroup()
        self.player = PlayerSprite(self.model, group)
        self.player.spawn(self.clock, self.meters_to_pixels)
        return group
        
    def _init_enemy_sprites(self) -> CharacterCameraGroup:
        """
        A helper method for creating the initial enemies sprite group.

        :return: a list of enemy sprites
        """
        
        group = CharacterCameraGroup()

        # Setting up dummy enemies
        for entity in self.model.world._entities:
            if isinstance(entity, Enemy):
                location = self.model.world.locate_entity(entity).as_tuple()
                location = pygame.math.Vector2(location) * self.meters_to_pixels
                dummy = DummySprite(location, entity)
                group.add(dummy)
            
        return group
    
    def _init_environment_sprites(self) -> CharacterCameraGroup:
        
        group = CharacterCameraGroup()
        
        for entity in self.model.world._entities:
            if isinstance(entity, Terrain):
                location = self.model.world.locate_entity(entity).as_tuple()
                location = pygame.math.Vector2(location) * self.meters_to_pixels
                size = pygame.math.Vector2(entity.size) * self.meters_to_pixels
                terrain = TerrainSprite(location, size, entity)
                group.add(terrain)
        
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
        help_text = StateText(
            (0, 0), 
            self.font, 
            f'Help is here. Use {Bindings.render(self.model.bindings.close_help)} to return.'
        )
        group.add(help_text)
        
        return group
    
    def _init_menu_sprites(self) -> pygame.sprite.Group:
        """
        A helper method for creating all the menu sprites.

        :return: a group of menu sprites
        """
        
        group = pygame.sprite.Group()
        
        menu_text = StateText(
            (self.screen.get_width() / 2, self.screen.get_height() / 2),
            self.font,
            f'You are in the Menu. '
            f'Use {Bindings.render(self.model.bindings.close_menu)} to go back to playing. '
            f'Use {Bindings.render(self.model.bindings.close_game)} to exit the game.',
            anchor="center"
        )
        group.add(menu_text)
        
        return group
    
    def _init_ui_sprites(self) -> pygame.sprite.Group:
        """
        A helper method for creating all of the UI sprites during the game.

        :return: a group of UI sprites
        """
        
        group = pygame.sprite.Group()
        
        # Setting up play text
        play_text = StateText(
            (0, self.screen.get_height() - self.font.get_height()),
            self.font,
            f'You are playing the game. {Bindings.render(self.model.bindings.open_help)} for help.'
        )
        group.add(play_text)
        
        # Setting up palette
        self.palette = PaletteSprite(
            (10, 10), 
            (
                pygame.display.get_window_size()[0] / 8,
                pygame.display.get_window_size()[1] / 20
            ),
            self.model.character._palette,
            self.clock
        )
        group.add(self.palette)
        
        return group
    
    def _init_title_screen_sprites(self) -> pygame.sprite.Group:
        """
        A helper method for creating all the title screen sprites.

        :return: _description_
        """
        
        group = pygame.sprite.Group()
        
        self.new_game_button = ButtonSprite(
            (self.screen.get_rect().centerx, self.screen.get_rect().centery + 50), 
            self.font, 
            "New Game"
        )
        group.add(self.new_game_button)
        
        self.load_game_button = ButtonSprite(
            (self.screen.get_rect().centerx, self.screen.get_rect().centery + 100), 
            self.font, 
            "Load Game"
        )
        #group.add(self.load_game_button)
        
        return group
    
    def _new_game(self):
        """
        Loads the game by initializing the model and
        generating appropriate sprites.
        """
        
        # Start a fresh game
        self.model.new_game()
        
        # Initialize some global variables
        self.meters_to_pixels = self.screen.get_width() / self.model.character._view_width

        # Create sprite groups
        self.attack_sprites = CharacterCameraGroup()
        self.enemy_sprites = self._init_enemy_sprites()
        self.terrain_sprites = self._init_environment_sprites()
        self.play_sprites = self._init_player_sprite()
        self.play_sprites.add(*self.enemy_sprites.sprites())
        self.play_sprites.add(*self.attack_sprites.sprites())
        self.play_sprites.add(*self.terrain_sprites.sprites())
        self.ui_sprites = self._init_ui_sprites()
        self.help_sprites = self._init_help_sprites()
        self.menu_sprites = self._init_menu_sprites()
    
    def initialize(self):
        """
        Sets up the pygame graphical display and loads graphical resources.
        """

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Mage Game')
        
        # Initialize graphics fields
        self.screen = pygame.display.set_mode((0, 0))
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font(None, 40)
        
        # Initialize title screen
        self.title_screen_sprites = self._init_title_screen_sprites()
        
        # Declaring the view initialized
        self.isinitialized = True

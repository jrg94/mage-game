import pygame

from .eventmanager import *
from .model import *


class MouseAndKeyboard:
    """
    Handles keyboard input.
    """

    class Bindings:
        """
        An inner class for defining key bindings using easy to read names.
        This object should be saved with the game state to preserve user settings.
        """

        def __init__(self):
            # Game buttons
            self.close_game = [pygame.K_ESCAPE]
            self.select_palette_item = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
            self.move_character = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_w]
            self.cast = [pygame.BUTTON_LEFT]
            
            # Menu buttons
            self.open_menu = [pygame.K_TAB]
            self.close_menu = [pygame.K_TAB]
            
            # Help buttons
            self.open_help = [pygame.K_F1]
            self.close_help = [pygame.K_ESCAPE, pygame.K_F1]

    def __init__(self, event_manager: EventManager, model: GameEngine):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.event_manager = event_manager
        event_manager.register_listener(self)
        self.model = model
        self.bindings = MouseAndKeyboard.Bindings()

    def notify(self, event: pygame.event.Event):
        """
        Receive events posted to the message queue. 

        :param event: the pygame event
        """

        if isinstance(event, TickEvent):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.event_manager.post(QuitEvent())
                if event.type == pygame.KEYDOWN:
                    currentstate = self.model.state.peek()
                    if currentstate == GameState.STATE_MENU:
                        self.key_down_menu(event)
                    if currentstate == GameState.STATE_PLAY:
                        self.key_down_play(event)
                    if currentstate == GameState.STATE_HELP:
                        self.key_down_help(event)
                    if currentstate == GameState.STATE_INTRO:
                        self.key_down_intro(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    currentstate = self.model.state.peek()
                    if currentstate == GameState.STATE_PLAY:
                        self.mouse_down_play(event)
                    if currentstate == GameState.STATE_INTRO:
                        self.mouse_down_intro(event)

    def key_down_menu(self, event: pygame.event.Event):
        """
        Handles menu key events. From the menu, the user
        can either quit the game or return to play. See
        bindings for defaults.

        :param event: the key press event
        """

        if event.key in self.bindings.close_game:
            self.event_manager.post(QuitEvent())
        elif event.key in self.bindings.close_menu:
            self.event_manager.post(StateChangeEvent(None))

    def key_down_help(self, event: pygame.event.Event):
        """
        Handles help key events. From the help page, the
        user can only return to play. See bindings for
        defaults.

        :param event: the key press event
        """

        if event.key in self.bindings.close_help:
            self.event_manager.post(StateChangeEvent(None))

    def key_down_play(self, event: pygame.event.Event):
        """
        Handles gameplay key events. While playing. the user
        can launch the main menu, the help menu, or propogate
        key presses to the view. See bindings for defaults.

        :param event: the key press event
        """
        if event.key in self.bindings.open_menu:
            self.event_manager.post(StateChangeEvent(GameState.STATE_MENU))
        elif event.key in self.bindings.open_help:
            self.event_manager.post(StateChangeEvent(GameState.STATE_HELP))
        elif event.key in self.bindings.select_palette_item:
            self.event_manager.post(PaletteSelectEvent(self.bindings.select_palette_item.index(event.key)))

    def key_down_intro(self, event: pygame.event.Event):
        """
        Handles title screen key events. From the title screen,
        the user can close the game. See key bindings for defaults.

        :param event: the key press event
        """
        if event.key == self.bindings.close_game:
            self.event_manager.post(StateChangeEvent(None))

    def mouse_down_play(self, event: pygame.event.Event):
        """
        Handles play mouse events.

        :param event: the mouse press event object
        """
        if event.button in self.bindings.cast:
            self.event_manager.post(CastEvent())

    def mouse_down_intro(self, event: pygame.event.Event):
        """
        Handles mouse press events on the title screen.

        :param event: the mouse press event object
        """
        self.event_manager.post(MouseEvent(event.button, event.pos))

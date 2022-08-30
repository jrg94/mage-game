import pygame

from .eventmanager import *
from .model import *


class MouseAndKeyboard:
    """
    Handles keyboard input.
    """

    def __init__(self, evManager: EventManager, model: GameEngine):
        """
        evManager (EventManager): Allows posting messages to the event queue.
        model (GameEngine): a strong reference to the game Model.
        """
        self.evManager = evManager
        evManager.register_listener(self)
        self.model = model

    def notify(self, event):
        """
        Receive events posted to the message queue. 
        """

        if isinstance(event, TickEvent):
            # Called for each game tick. We check our keyboard presses here.
            for event in pygame.event.get():
                # handle window manager closing our window
                if event.type == pygame.QUIT:
                    self.evManager.post(QuitEvent())
                # handle key down events
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
        Handles menu key events.
        """

        if event.key == pygame.K_ESCAPE:
            self.evManager.post(QuitEvent())
        if event.key == pygame.K_TAB:
            self.evManager.post(StateChangeEvent(None))
        if event.key == pygame.K_SPACE:
            self.evManager.post(StateChangeEvent(GameState.STATE_PLAY))

    def key_down_help(self, event: pygame.event.Event):
        """
        Handles help key events.
        """

        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
            self.evManager.post(StateChangeEvent(None))

    def key_down_play(self, event: pygame.event.Event):
        """
        Handles gameplay key events. While playing, pressing tab
        should launch the menu. Meanwhile, pressing F1 should launch
        the help menu. Other key presses are automatically passed to
        the event manager to be used by the view directly.
        """
        if event.key == pygame.K_TAB:
            self.evManager.post(StateChangeEvent(GameState.STATE_MENU))
        elif event.key == pygame.K_F1:
            self.evManager.post(StateChangeEvent(GameState.STATE_HELP))
        else:
            self.evManager.post(KeyboardEvent(event.key, event.unicode))
            
    def key_down_intro(self, event: pygame.event.Event):
        """
        Handles title screen key events. At the title screen,
        escape will close the game.
        
        :param event: the key press event
        """
        if event.key == pygame.K_ESCAPE:
            self.evManager.post(StateChangeEvent(None))

    def mouse_down_play(self, event: pygame.event.Event):
        """
        Handles play mouse events.
        
        :param event: the mouse press event object
        """
        self.evManager.post(MouseEvent(event.button, event.pos))
        
    def mouse_down_intro(self, event: pygame.event.Event):
        """
        Handles mouse press events.

        :param event: the mouse press event object
        """
        self.evManager.post(MouseEvent(event.button, event.pos))

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
        evManager.RegisterListener(self)
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
                    self.evManager.Post(QuitEvent())
                # handle key down events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.evManager.Post(StateChangeEvent(None))
                    else:
                        currentstate = self.model.state.peek()
                        if currentstate == GameState.STATE_MENU:
                            self.key_down_menu(event)
                        if currentstate == GameState.STATE_PLAY:
                            self.key_down_play(event)
                        if currentstate == GameState.STATE_HELP:
                            self.key_down_help(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    currentstate = self.model.state.peek()
                    if currentstate == GameState.STATE_PLAY:
                        self.mouse_down_play(event)
                    if currentstate == GameState.STATE_INTRO:
                        self.mouse_down_intro(event)

    def key_down_menu(self, event):
        """
        Handles menu key events.
        """

        # escape pops the menu
        if event.key == pygame.K_ESCAPE:
            self.evManager.Post(StateChangeEvent(None))
        # space plays the game
        if event.key == pygame.K_SPACE:
            self.evManager.Post(StateChangeEvent(GameState.STATE_PLAY))

    def key_down_help(self, event):
        """
        Handles help key events.
        """

        # space, enter or escape pops help
        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
            self.evManager.Post(StateChangeEvent(None))

    def key_down_play(self, event):
        """
        Handles play key events.
        """
        if event.key == pygame.K_ESCAPE:
            self.evManager.Post(StateChangeEvent(None))
        # F1 shows the help
        if event.key == pygame.K_F1:
            self.evManager.Post(StateChangeEvent(GameState.STATE_HELP))
        else:
            self.evManager.Post(KeyboardEvent(event.key, event.unicode))

    def mouse_down_play(self, event):
        """
        Handles play mouse events.
        """
        self.evManager.Post(MouseEvent(event.button, event.pos))
        
    def mouse_down_intro(self, event):
        self.evManager.Post(MouseEvent(event.button, event.pos))

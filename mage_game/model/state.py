from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

from build.lib.mage_game.model.world import WorldPoint

from ..eventmanager import *
from .bindings import Bindings
from .character import Character
from .world import Entity, World


class GameState(Enum):
    """
    A helpful enum for determining the current state
    of the game.
    """
    
    STATE_INTRO = auto()
    STATE_MENU = auto()
    STATE_HELP = auto()
    STATE_ABOUT = auto()
    STATE_PLAY = auto()


class GameEngine:
    """
    Tracks the game state.

    :param event_manager: the event manager.
    """

    def __init__(self, event_manager: EventManager):
        self.event_manager: EventManager = event_manager
        self.event_manager.register_listener(self)
        self.running: bool = False
        self.state: StateMachine = StateMachine()
        self.bindings: Bindings = Bindings()
        self.character: Character = None
        self.world: World = None

    def notify(self, event: EventManager) -> None:
        """
        Called by an event in the message queue. 

        :param event: the current event.
        """

        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.event_manager.post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def new_game(self) -> None:
        """
        Loads game data, if it exists. Creates a new game
        otherwise. 
        """
        self.character = Character.new_character()
        self.world = World()
        self.world.add_entity(self.character)
        for _ in range(5):
            x = random.randint(-5, 5)
            y = random.randint(-5, 5)
            enemy = Enemy(WorldPoint(x, y), (1, 1))
            self.world.add_entity(enemy)
        
    def run(self) -> None:
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.event_manager.post(InitializeEvent())
        self.state.push(GameState.STATE_INTRO)
        while self.running:
            newTick = TickEvent()
            self.event_manager.post(newTick)


class StateMachine(object):
    """
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    """

    def __init__(self):
        self.state_stack = []

    def peek(self) -> int | None:
        """
        Without altering the stack, returns the current state.

        :return: the current state or None if the stack is empty.
        """
        try:
            return self.state_stack[-1]
        except IndexError:
            return None

    def pop(self) -> int | None:
        """
        Remove the top state from the stack and return it.

        :return: the current state or None if the stack is empty.
        """
        try:
            self.state_stack.pop()
            return len(self.state_stack) > 0
        except IndexError:
            return None

    def push(self, state) -> int:
        """
        Push a new state onto the stack.

        :param state: the new state to push on the stack.
        :return: the new state.
        """
        self.state_stack.append(state)
        return state


@dataclass
class Enemy(Entity):
    """
    The Enemy class represents enemy data.

    :param _hp: the health of the enemy
    """

    _hp: int = 10

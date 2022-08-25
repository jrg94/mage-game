from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ..eventmanager import *
from .character import Character


class GameState(Enum):
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
        self.event_manager.RegisterListener(self)
        self.running: bool = False
        self.state: StateMachine = StateMachine()
        self.world_width: int = 100  # in meters
        self.enemies: list[Enemy] = [Enemy()]
        self.character = Character.new_character()

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
                    self.event_manager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def run(self) -> None:
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.event_manager.Post(InitializeEvent())
        self.state.push(GameState.STATE_MENU)
        while self.running:
            newTick = TickEvent()
            self.event_manager.Post(newTick)


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
class Enemy:
    """
    The Enemy class represents enemy data.

    :param _hp: the health of the enemy
    """

    _hp: int = 10

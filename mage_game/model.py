import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import ClassVar

from eventmanager import *


class GameEngine(object):
    """
    Tracks the game state.
    """

    def __init__(self, evManager: EventManager):
        """
        evManager (EventManager): Allows posting messages to the event queue.

        Attributes:
        running (bool): True while the engine is online. Changed via QuitEvent().
        """

        self.evManager: EventManager = evManager
        evManager.RegisterListener(self)
        self.running: bool = False
        self.state: StateMachine = StateMachine()
        self.palette: Palette = Palette()
        self.world_width: int = 100  # in meters

    def notify(self, event):
        """
        Called by an event in the message queue. 
        """

        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, StateChangeEvent):
            # pop request
            if not event.state:
                # false if no more states are left
                if not self.state.pop():
                    self.evManager.Post(QuitEvent())
            else:
                # push a new state on the stack
                self.state.push(event.state)

    def run(self):
        """
        Starts the game engine loop.

        This pumps a Tick event into the message queue for each loop.
        The loop ends when this object hears a QuitEvent in notify(). 
        """
        self.running = True
        self.evManager.Post(InitializeEvent())
        self.state.push(STATE_MENU)
        while self.running:
            newTick = TickEvent()
            self.evManager.Post(newTick)


# State machine constants for the StateMachine class below
STATE_INTRO = 1
STATE_MENU = 2
STATE_HELP = 3
STATE_ABOUT = 4
STATE_PLAY = 5


class StateMachine(object):
    """
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    """

    def __init__(self):
        self.statestack = []

    def peek(self):
        """
        Returns the current state without altering the stack.
        Returns None if the stack is empty.
        """
        try:
            return self.statestack[-1]
        except IndexError:
            # empty stack
            return None

    def pop(self):
        """
        Returns the current state and remove it from the stack.
        Returns None if the stack is empty.
        """
        try:
            self.statestack.pop()
            return len(self.statestack) > 0
        except IndexError:
            # empty stack
            return None

    def push(self, state):
        """
        Push a new state onto the stack.
        Returns the pushed value.
        """
        self.statestack.append(state)
        return state


class Element(Enum):
    """
    A handy enum for the spell elements in the game.
    """

    FIRE = auto(), (255, 0, 0)
    WATER = auto(), (0, 0, 255)
    EARTH = auto(), (255, 255, 0)
    AIR = auto(), (0, 255, 255)
    LIGHT = auto(), (255, 255, 255)
    DARK = auto(), (0, 0, 0)
    NONE = auto(), (0, 255, 0)

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, color: tuple = (255, 255, 255)):
        self._color = color

    def __str__(self):
        return self.value

    @property
    def color(self):
        return self._color


@dataclass()
class Projectile:
    """
    A projectile-based spell.

    :param Element element: the element of the spell.
    :param int speed_level: the speed level of the spell.
    :param int radius_level: the radius level of the spell.
    :param int distance_level: the distance level of the spell.
    :param int damage_level: the damage level of the spell.
    :cvar float BASE_SPEED: the base speed of the spell in meters per second.
    :cvar float BASE_RADIUS: the base radius of the spell in meters.
    :cvar float BASE_DISTANCE: the base distance of the spell in meters.
    :cvar int BASE_DAMAGE: the base damage of the spell in hit points.
    :cvar float MAX_COOLDOWN: the maximum cooldown of the spell in seconds.
    """

    _element: Element = Element.NONE
    _speed_level: int = 1
    _radius_level: int = 1
    _distance_level: int = 1
    _damage_level: int = 1
    _cooldown_level: int = 1

    BASE_SPEED: ClassVar[float] = 5.0
    BASE_RADIUS: ClassVar[float] = .25
    BASE_DISTANCE: ClassVar[float] = 10.0
    BASE_DAMAGE: ClassVar[int] = 1
    MAX_COOLDOWN: ClassVar[float] = 2.0

    @staticmethod
    def scale(level: int, base: float) -> float:
        """
        A helper function that scales a value based on a base value.

        :param level: the level of the spell parameter.
        :param base: the base value of the spell parameter.
        """
        return math.log(level, 2) * base + base
    
    def element(self) -> Element:
        """
        Retrieves the element of the spell.
        
        :return: the element of the spell.
        """
        return self._element

    def speed(self) -> float:
        """
        Computes the speed of the projectile in meters per second.
        Speed, as with all other spell parameters, follows a logarithmic curve (base 2).
        If the base speed is 10 meters per second, the scaling might look as follows:

            - Speed level 1: 10 meters per second
            - Speed level 2: 20 meters per second
            - Speed level 3: ~25.85 meters per second
            - Speed level 4: 30 meters per second
            
        :return: the speed of the projectile in meters per second.
        """
        return self.scale(self._speed_level, self.BASE_SPEED)

    def radius(self) -> float:
        return self.scale(self._radius_level, self.BASE_RADIUS)

    def distance(self) -> float:
        return self.scale(self._distance_level, self.BASE_DISTANCE)

    def damage(self) -> int:
        return math.ceil(self.scale(self._damage_level, self.BASE_DAMAGE))

    def cooldown(self) -> float:
        # TODO: this increases cooldown
        return self.scale(self._cooldown_level, self.MAX_COOLDOWN)


@dataclass
class PaletteItem:
    """
    Represents a single item in the game palette.

    :param Projectile spell: the spell that this item represents.
    :param float cooldown: the remaining time on the cooldown of the spell in milliseconds.
    """

    spell: Projectile = field(default_factory=Projectile)
    cooldown: float = Projectile.MAX_COOLDOWN * 1000

    def can_use(self) -> bool:
        """
        Returns True if the palette item is ready to be used.
        """
        return self.cooldown <= 0.0

    def reset_cooldown(self, cooldown: float):
        """
        Resets the cooldown of the palette item.

        :cooldown: the cooldown of the palette item in milliseconds.
        """
        self.cooldown = cooldown


@dataclass
class Palette:
    """
    Represents the game palette.

    :param list[PaletteItem] items: the list of spells in the palette.
    :param int current_spell_index: the index of the active spell in the palette.
    """

    items: list[PaletteItem] = field(default_factory=lambda: [
        PaletteItem(Projectile(Element.FIRE)),
        PaletteItem(Projectile(Element.WATER)),
        PaletteItem(Projectile(Element.EARTH)),
        PaletteItem(Projectile(Element.AIR)),
    ])
    current_spell_index: int = 0

    def get_active_item(self) -> PaletteItem:
        """
        Retrieves the currently active spell from the palette.

        :returns: the currently active spell.
        """
        return self.items[self.current_spell_index]

    def update_cooldowns(self, dt: float) -> bool:
        """
        Lowers cooldowns for all spells in the palette.

        :param float dt: the time in milliseconds since the last update.
        """
        for palette_item in self.items:
            palette_item.cooldown -= dt
            if palette_item.cooldown <= 0:
                palette_item.cooldown = 0

    def can_cast_active_spell(self) -> bool:
        """
        Verifies that the currently active spell can be cast.

        :returns: True if the spell can be cast, False otherwise.
        """
        return self.get_active_item().can_use()

    def reset_active_spell_cooldown(self):
        """
        Resets the cooldown of the currently active spell.
        """
        self.get_active_item().reset_cooldown(self.get_active_item().cooldown() * 1000)

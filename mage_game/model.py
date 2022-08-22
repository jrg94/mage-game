import math
from dataclasses import dataclass, field
from enum import Enum, auto

from eventmanager import *


# Spell attribute constants
BASE_SPEED: float = 5.0  # the base speed of the spell in meters per second.
BASE_RADIUS: float = .25  # the base radius of the spell in meters.
BASE_DISTANCE: float = 10.0  # the base distance of the spell in meters.
BASE_DAMAGE: int = 1  # the base damage of the spell in hit points.
BASE_COOLDOWN: float = 2.0  # the base cooldown of the spell in seconds.
BASE_CAST_TIME: float = 2.0  # the base cast time of the spell in seconds.
BASE_CRIT_CHANCE: float = .05  # the base chance of a critical hit.

# State machine constants for the StateMachine class below
STATE_INTRO = 1
STATE_MENU = 2
STATE_HELP = 3
STATE_ABOUT = 4
STATE_PLAY = 5


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
        self.state.push(STATE_MENU)
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
    def color(self) -> tuple:
        """
        Retrieves the color of the element.

        :return: the color of the element in (r, g, b) format.
        """
        return self._color


class SpellAttribute(Enum):
    DAMAGE = auto()
    CRIT_CHANCE = auto()
    COOLDOWN = auto()
    CAST_TIME = auto()
    DISTANCE = auto()
    RADIUS  = auto()
    SPEED = auto()


@dataclass
class AttributeTracking:
    """
    A handy class for tracking spell attributes.
    
    :param _attribute: the type of attribute to track.
    :param _base: the base value of the attribute.
    :param _level: the level of the attribute.
    :param _events: the number of qualifying events to increase the attribute.
    """
    
    _attribute: SpellAttribute
    _base: float
    _level: int = 1
    _events: int = 0
    _scale: str = "logarithmic"
    
    def effective_value(self):
        """
        A helper function that scales a value based on a base value.
        The effective value can be computed in a variety of ways. Typically,
        values that scale up will follow a logarithmic growth curve while 
        values that scale down will follow an inverse growth curve.

        :return: the scaled value of the spell attribute.
        """
        if self._scale == "logarithmic":
            return math.log(self._level, 2) * self._base + self._base
        elif self._scale == "inverse":
            return 1 / (self._level) * self._base


@dataclass
class Projectile:
    """
    A projectile-based spell.

    :param Element _element: the element of the spell.
    :param int _speed: the speed attribute of the spell.
    :param int _radius: the radius attribute of the spell.
    :param int _distance: the distance attribute of the spell.
    :param int _damage: the damage attribute of the spell.
    """

    _element: Element = Element.NONE
    _speed: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.SPEED, BASE_SPEED))
    _radius: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.RADIUS, BASE_RADIUS))
    _distance: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.DISTANCE, BASE_DISTANCE))
    _damage: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.DAMAGE, BASE_DAMAGE))
    _cooldown: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.COOLDOWN, BASE_COOLDOWN, _scale="inverse"))
    _cast_time: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.CAST_TIME, BASE_CAST_TIME, _scale="inverse"))
    _crit_chance: AttributeTracking = field(default_factory=lambda: AttributeTracking(SpellAttribute.CRIT_CHANCE, BASE_CRIT_CHANCE))


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
        return self._speed.effective_value()

    def radius(self) -> float:
        """
        Computes the radius of the projectile in meters. See speed() for more information
        on how the scaling works.

        :return: the radius of the projectile in meters.
        """
        return self._radius.effective_value()

    def distance(self) -> float:
        """
        Computes the distance the projectile travels in meters. See speed() for more information
        on how the scaling works.

        :return: the distance the projectile travels in meters.
        """
        return self._distance.effective_value()

    def damage(self) -> int:
        """
        Computes the damage of the projectile in hit points. See speed() for more information
        on how the scaling works.

        :return: the damage of the projectile in hit points.
        """
        return math.ceil(self._damage.effective_value())

    def cooldown(self) -> float:
        """
        Computes the cooldown of the projectile in seconds. 

        :return: the cooldown of the projectile in seconds.
        """
        # TODO: this increases cooldown
        return self._cooldown.effective_value()
    
    def cast_time(self) -> float:
        return self._cast_time.effective_value()
    
    def crit_chance(self) -> float:
        return self._crit_chance.effective_value()


@dataclass
class PaletteItem:
    """
    Represents a single item in the game palette.

    :param Projectile spell: the spell that this item represents.
    :param float cooldown: the remaining time on the cooldown of the spell in milliseconds.
    """

    _spell: Projectile = field(default_factory=Projectile)
    _cooldown: float = 0.0

    def can_use(self) -> bool:
        """
        Returns True if the palette item is ready to be used.

        :return: True if the palette item is ready to be used.
        """
        return self._cooldown <= 0.0

    def reset_cooldown(self, cooldown: float) -> None:
        """
        Resets the cooldown of the palette item.

        :param cooldown: the cooldown of the palette item in milliseconds.
        """
        self._cooldown = cooldown

    def get_spell(self) -> Projectile:
        """
        Returns the spell of the palette item.

        :return: the spell of the palette item.
        """
        return self._spell


@dataclass
class Palette:
    """
    Represents the game palette.

    :param list[PaletteItem] items: the list of spells in the palette.
    :param int current_spell_index: the index of the active spell in the palette.
    """

    _items: list[PaletteItem] = field(default_factory=list)
    _current_item_index: int = 0
    _casting_time: int = 0

    def get_active_item(self) -> PaletteItem:
        """
        Retrieves the currently active spell from the palette.

        :return: the currently active spell.
        """
        return self._items[self._current_item_index]

    def get_active_item_index(self) -> int:
        """
        Retrieves the index of the currently active spell from the palette.

        :return: the index of the currently active spell.
        """
        return self._current_item_index

    def update_cooldowns(self, dt: float) -> None:
        """
        Lowers cooldowns for all spells in the palette.

        :param float dt: the time in milliseconds since the last update.
        """
        for palette_item in self._items:
            palette_item._cooldown -= dt
            if palette_item._cooldown <= 0:
                palette_item._cooldown = 0

    def can_cast_active_spell(self) -> bool:
        """
        Verifies that the currently active spell can be cast.

        :return: True if the spell can be cast, False otherwise.
        """
        return self.get_active_item().can_use() and self._casting_time <= 0

    def reset_active_spell_cooldown(self) -> None:
        """
        Resets the cooldown of the currently active spell.
        """
        self.get_active_item().reset_cooldown(
            self.get_active_item().get_spell().cooldown() * 1000)

    def get_items(self) -> list[PaletteItem]:
        """
        Retrieves the list of spells in the palette.

        :return: the list of spells in the palette.
        """
        return self._items

    def set_active_palette_item(self, index: int) -> None:
        """
        Sets the currently active spell in the palette.

        :param index: the index of the spell in the palette.
        """
        self._current_item_index = index
        
    def reset_casting_time(self) -> None:
        self._casting_time = self.get_active_item().get_spell().cast_time() * 1000
        
    def update_casting_time(self, dt) -> None:
        self._casting_time -= dt
        if self._casting_time <= 0:
            self._casting_time == 0
            
    def get_remaining_casting_time(self) -> int:
        return self._casting_time
    
@dataclass
class Enemy:
    _hp: int = 100
    
@dataclass
class Character:
    spell_book: list = field(default_factory=list)
    palette: Palette = field(default_factory=Palette)
    
    @staticmethod
    def new_character():
        character = Character()
        character.spell_book.extend([
            Projectile(Element.FIRE),
            Projectile(Element.WATER),
            Projectile(Element.EARTH),
            Projectile(Element.AIR),
            Projectile(Element.LIGHT),
            Projectile(Element.DARK),
        ])
        character.palette.get_items().extend([
            PaletteItem(spell) for spell in character.spell_book[:4]
        ])
        return character

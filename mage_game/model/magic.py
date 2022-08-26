import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


class Element(Enum):
    """
    A handy enum for the spell elements in the game.
    
    :member FIRE: the oxygen powered burny element (red).
    :member WATER: the wet element (blue).
    :member EARTH: the dirty element (orange).
    :member AIR: the invisible flowy element (turqouise).
    :member LIGHT: the holy element (white).
    :member DARK: the evil element (purple).
    :member NONE: the neutral element (green)
    """

    FIRE = auto(), (255, 0, 0)
    WATER = auto(), (0, 0, 255)
    EARTH = auto(), (255, 255, 0)
    AIR = auto(), (0, 255, 255)
    LIGHT = auto(), (255, 255, 255)
    DARK = auto(), (255, 0, 255)
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
    """
    SpellAttribute is an enum class that is meant to represent
    the different types of attributes a spell may have. I 
    specifically created this class to ensure that new attributes
    could be easily added at a later date. Then, classes that
    depend on SpellAttribute can implement simple methods that
    can look up attributes by enum, rather than hardcoding attribute
    methods for every type of attribute.

    .. note::
       It is very important that spells using SpellAttribute follow
       the units outlined in the docs below. The units used in the
       view may be different, so pay attention to when conversions
       are needed.

    :member DAMAGE: damage refers to the damage of a spell in hp.
       This does not necessarily mean an enemy will take that exact 
       amount of damage due to resistances, but it should give a
       rough max damage.
    :member CRIT_CHANCE: crit chance refers to the likelihood of
       a critical hit occuring as a ratio (e.g., .05). Critical
       hits are scaled by CRIT_DAMAGE.
    :member CRIT_DAMAGE: crit damage refers to the ratio of 
       DAMAGE to increase a hit by (e.g., .5).
    :member COOLDOWN: cooldown refers to the time the player
       has to wait in seconds before they can cast the spell 
       again.
    :member CAST_TIME: cast time refers to the amount of time it
       takes to charge up a spell in seconds. 
    :member DISTANCE: distance refers to the distance that a spell
       travels in meters.
    :member RADIUS: radius refers to the size of a spell in meters.
    :member SPEED: speed refers to the travel speed of a spell in
       meters per second.
    :member COUNT: coutn refers to the number of instances of a spell 
       (e.g., # of projectiles)
    """

    DAMAGE = auto(), 1
    CRIT_CHANCE = auto(), .05
    CRIT_DAMAGE = auto(), .25
    COOLDOWN = auto(), 2.0
    CAST_TIME = auto(), 2.0
    DISTANCE = auto(), 10.0
    RADIUS = auto(), .1
    SPEED = auto(), 5.0
    COUNT = auto(), 1

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, base: float = 1):
        self._base = base

    def __str__(self):
        return self.value

    @property
    def base_value(self) -> float:
        return self._base


@dataclass
class AttributeTracking:
    """
    A handy class for tracking spell attributes.

    :param SpellAttribute attribute: the type of attribute to track.
    :param int _level: the level of the attribute.
    :param int _events: the number of qualifying events to increase the attribute.
    :param str _scale: the function used for scaling.
    :param Callable _post: a function that can be used to post process the data.
    :param str _units: the units of the attribute.
    """

    attribute: SpellAttribute
    _level: int = 1
    _events: int = 0
    _scale: str = "logarithmic"
    _post: Callable = lambda x: x
    _units: str = "m"

    def level(self) -> int:
        """
        Retrieves the current level of this attribute.

        :return: the level of the attribute as an integer.
        """
        return self._level

    def effective_value(self) -> float:
        """
        A helper function that scales a value based on a base value.
        The effective value can be computed in a variety of ways. Typically,
        values that scale up will follow a logarithmic growth curve while 
        values that scale down will follow an inverse growth curve.

        :return: the scaled value of the spell attribute.
        """
        if self._scale == "logarithmic":
            return self._post(math.log(self._level, 2) * self.attribute.base_value + self.attribute.base_value)
        elif self._scale == "inverse":
            return self._post(1 / (self._level) * self.attribute.base_value)

    def trigger_event(self) -> None:
        """
        Call this method when a player meets the requirements to trigger an event.
        Events are used to level up abilities. The current scaling of abilities
        works on the doubling principle on increments of 10:

            - Level 1 -> 2: Perform 10 events
            - Level 2 -> 3: Perform 20 events (on top of the original 10)
            - Level 3 -> 4: Perform 40 events (on top of the previous 30)
        """
        self._events += 1
        self._level = int(math.log((self._events // 5) + 2, 2))

    def events_to_next_level(self) -> int:
        """
        A handy function for computing the inverse of the level function. 
        This will tell you how many more events you must trigger before you
        can get to the next level.

        :return: the number of events need to reach the next level.
        """
        next_level = self._level + 1
        return ((2 ** next_level) - 2) * 5 - self._events


@dataclass
class Projectile:
    """
    A projectile-based spell.

    :param Element _element: the element of the spell.
    :param dict[SpellAttribute, AttributeTracking] _attributes: a mapping of attribute types to their record keeping objects
    """

    _element: Element = Element.NONE
    _attributes: dict[SpellAttribute: AttributeTracking] = field(default_factory=lambda: {
        SpellAttribute.SPEED: AttributeTracking(SpellAttribute.SPEED, _units="m/s"),
        SpellAttribute.RADIUS: AttributeTracking(SpellAttribute.RADIUS),
        SpellAttribute.DISTANCE: AttributeTracking(SpellAttribute.DISTANCE),
        SpellAttribute.DAMAGE: AttributeTracking(SpellAttribute.DAMAGE, _post=math.ceil, _units="hp"),
        SpellAttribute.COOLDOWN: AttributeTracking(SpellAttribute.COOLDOWN, _scale="inverse", _units="s"),
        SpellAttribute.CAST_TIME: AttributeTracking(SpellAttribute.CAST_TIME, _scale="inverse", _units="s"),
        SpellAttribute.CRIT_CHANCE: AttributeTracking(SpellAttribute.CRIT_CHANCE, _units="%")
    })
    # TODO: add a path field to dictate how the projectile should travel

    def get_tracking(self, attribute: SpellAttribute) -> AttributeTracking | None:
        """
        Retrieves an attribute based on the enum.

        :param attribute: a spell attribute enum used for differentiating spell attributes.
        :return: the attribute or None
        """
        return self._attributes.get(attribute)

    def get_attribute(self, attribute: SpellAttribute) -> float:
        """
        Retrieves the value of an attribute.

        :param attribute: a spell attribute enum used for differentiating spell attributes.
        :return: the value of the attribute
        """
        return self.get_tracking(attribute).effective_value()

    def element(self) -> Element:
        """
        Retrieves the element of the spell.

        :return: the element of the spell.
        """
        return self._element

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar


class Element(Enum):
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


@dataclass
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
    """

    element: Element = Element.NONE
    speed_level: int = 1
    radius_level: int = 1
    distance_level: int = 1
    damage_level: int = 1

    BASE_SPEED: ClassVar[float] = 5.0
    BASE_RADIUS: ClassVar[float] = .25
    BASE_DISTANCE: ClassVar[float] = 10.0
    BASE_DAMAGE: ClassVar[int] = 1

    @staticmethod
    def scale(level: int, base: float) -> float:
        """
        A helper function that scales a value based on a base value.

        :param level: the level of the spell parameter.
        :param base: the base value of the spell parameter.
        """
        return math.log(level, 2) * base + base

    def speed(self) -> float:
        """
        Computes the speed of the projectile in meters per second.
        Speed, as with all other spell parameters, follows a logarithmic curve (base 2).
        If the base speed is 10 meters per second, the scaling might look as follows:

            - Speed level 1: 10 meters per second
            - Speed level 2: 20 meters per second
            - Speed level 3: ~25.85 meters per second
            - Speed level 4: 30 meters per second
        """
        return self.scale(self.speed_level, self.BASE_SPEED)

    def radius(self) -> float:
        return self.scale(self.radius_level, self.BASE_RADIUS)
    
    def distance(self) -> float:
        return self.scale(self.distance_level, self.BASE_DISTANCE)
    
    def damage(self) -> float:
        return self.scale(self.damage_level, self.BASE_DAMAGE)

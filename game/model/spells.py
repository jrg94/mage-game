from enum import Enum, auto
from dataclasses import dataclass
import math
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
    
    :param element: the element of the spell.
    :param speed_level: the speed level of the spell.
    :param radius_level: the radius level of the spell.
    :param distance_level: the distance level of the spell.
    :param damage_level: the damage level of the spell.
    :cvar BASE_SPEED: the base speed of the spell in meters per second.
    """
    
    element: Element = Element.NONE
    speed_level: int = 1
    radius_level: int = 1
    distance_level: int = 1
    BASE_SPEED: ClassVar[int] = 5
    
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
        return math.log(self.speed_level, 2) * self.BASE_SPEED + self.BASE_SPEED

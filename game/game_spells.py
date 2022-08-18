from enum import Enum, auto

class Element(Enum):
    FIRE = auto(), (255, 0, 0)
    WATER = auto(), (0, 0, 255)
    EARTH = auto(), (255, 255, 0)
    AIR = auto(), (0, 255, 255)
    LIGHT = auto(), (0, 0, 0)
    DARK = auto(), (255, 255, 255)
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

class Projectile():
    def __init__(self, element: Element = Element.NONE):
        self.element = element
        self.speed_level = 1
        self.radius_level = 1
        self.distance_level = 1
        
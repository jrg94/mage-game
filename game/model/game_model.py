from model import spells, pallette
from dataclasses import dataclass

@dataclass
class GameState:
    palette: pallette.Palette = pallette.Palette()
    world_width: int = 100 # in meters

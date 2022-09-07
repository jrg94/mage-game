import json
import pathlib
import pygame
from enum import Enum

from ..model.enemies import Enemy
from ..model.tiles import Terrain
from ..model.world import World, WorldPoint

ASSET_PATH = pathlib.Path("assets")
MAP_PATH = ASSET_PATH / "maps"
SPRITE_PATH = ASSET_PATH / "sprites"
MAP_SUFFIX = ".json"


class MapConst(str, Enum):
    COORDINATES = "coordinates"
    ENEMIES = "enemies"
    SIZE = "size"
    TERRAIN = "terrain"


def load_sprite(sprite_folder: str, sprite_name: str, id: int = None) -> pygame.Surface:
    sprite_path = (SPRITE_PATH / sprite_folder / f"{sprite_name}{id or ''}").with_suffix(".png")
    return pygame.image.load(sprite_path)


def load_map(map_name: str) -> World:
    """
    Generates a map from a JSON file.

    :param map_name: the name of the map
    :return: the map as a World object
    """
    map_path = (MAP_PATH / map_name).with_suffix(MAP_SUFFIX)
    world = World()
    with open(map_path) as map_file:
        map: dict = json.load(map_file)
        entities: list[dict] = map[MapConst.TERRAIN]
        for entity in entities:
            world.add_entity(Terrain(
                WorldPoint(*entity[MapConst.COORDINATES]),
                tuple(entity[MapConst.SIZE])
            ))
        enemies: list[dict] = map[MapConst.ENEMIES]
        for enemy in enemies:
            world.add_entity(Enemy(
                WorldPoint(*enemy[MapConst.COORDINATES]),
                tuple(entity[MapConst.SIZE])
            ))
    return world

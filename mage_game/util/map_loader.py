import json
from enum import Enum

from ..model.enemies import Enemy
from ..model.tiles import Terrain
from ..model.world import World, WorldPoint


class MapConst(str, Enum):
    COORDINATES = "coordinates"
    ENEMIES = "enemies"
    SIZE = "size"
    TERRAIN = "terrain"


def load_map(path: str) -> World:
    """
    Generates a map from a JSON file.

    :param path: the path to a json file
    :return: the map as a World object
    """
    world = World()
    with open(path) as map_file:
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

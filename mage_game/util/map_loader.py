import json
from enum import Enum

from ..model.tiles import Terrain
from ..model.world import World, WorldPoint


class MapConst(str, Enum):
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
                WorldPoint(*entity["coordinates"]),
                tuple(entity["size"])
            ))
    return world

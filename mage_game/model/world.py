from dataclasses import dataclass

class World(dict):
    """
    Uses the built-in dict to represent the game world.
    The game world works by storing integer coordinates.
    To keep things simple, one integer represents a millimeter.
    Therefore, the smallest unit of length in the game is
    a millimeter.
    """
    
    def add_entity(self, entity: object, location: tuple[int, int]):
        """
        Adds an entity to the World.

        :param entity: some object
        :param location: the location of the object in millimeters
        """
        self[location] = entity
        
    def locate_entity(self, entity) -> tuple | None:
        for key, value in self.items():
            if entity == value:
                return key
        return None
        
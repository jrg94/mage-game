from dataclasses import dataclass

class World(dict):
    """
    Uses the built-in dict to represent the game world.
    The game world works by storing integer coordinates.
    To keep things simple, one integer represents a millimeter.
    Therefore, the smallest unit of length in the game is
    a millimeter.
    
    Currently, this object is only used to setup initial conditions
    of the world. It would be nice for this to be a permanent
    representation of the world but using coordinates as keys
    seems somewhat silly for that. This will probably be more
    useful for level development than a live model of the world.
    """
    
    def add_entity(self, entity: object, location: tuple[int, int]):
        """
        Adds an entity to the World.

        :param entity: some object
        :param location: the location of the object in millimeters
        """
        self[location] = entity
        
    def locate_entity(self, entity) -> tuple | None:
        """
        Performs a reverse dictionary lookup.

        :param entity: an object to be looked up
        :return: the location of that object if it exists. None, otherwise.
        """
        for key, value in self.items():
            if entity == value:
                return key
        return None
        
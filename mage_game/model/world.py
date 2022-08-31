from dataclasses import dataclass, field


@dataclass
class WorldPoint:
    """
    Represents a point in our game world. Our game is 2D,
    so points are composed of XY coordinates.

    :param x: the x-coordinate
    :param y: the y-coordinate
    """
    x: float = 0
    y: float = 0
    
    def as_tuple(self):
        return (self.x, self.y)
    
@dataclass
class Entity:
    """
    An entity is any physical object in our game with
    a position in the game world. 
    
    :param coordinates: the XY coordinate for this entity
    """
    coordinates: WorldPoint
    size: tuple
    
    def move_entity(self, x_shift: float, y_shift: float) -> None:
        """
        Moves this entity by some x and y offset.

        :param x_shift: the x-value to add to the x-coordinate
        :param y_shift: the y-value to add to the y-coordinate
        """
        self.coordinates.x += x_shift
        self.coordinates.y += y_shift
        
    def teleport_entity(self, x: float, y: float):
        """
        Teleports this entity to some x and y coordinate, overwriting
        the existing coordinates.

        :param x: the new x-coordinate
        :param y: the new y-coordinate
        """
        self.coordinates.x = x
        self.coordinates.y = y

@dataclass
class World:
    """
    Represents the game world. This object allows use to track
    the location of various entities on an arbitrary XY coordinate
    system. Useful when setting up the world and tracking the
    locations of entities on the backend (i.e., not in pixel
    units). 
    
    :param _entities: a list of entities in the world. 
    """
    
    _entities: list[Entity] = field(default_factory=lambda: list())
    
    def add_entity(self, entity: Entity) -> None:
        """
        Adds an entity to the World.

        :param entity: some object
        """
        self._entities.append(entity)
        
    def locate_entity(self, entity) -> WorldPoint | None:
        """
        Searches the world for the entity before returning its location.

        :param entity: an object to be looked up
        :return: the location of that object if it exists. None, otherwise.
        """
        for item in self._entities:
            if entity == item:
                return item.coordinates
        return None
        
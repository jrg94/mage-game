from dataclasses import dataclass, field


@dataclass
class WorldPoint:
    x: float = 0
    y: float = 0
    
    def as_tuple(self):
        return (self.x, self.y)
    
@dataclass
class Entity:
    coordinates: WorldPoint = field(default_factory=lambda: WorldPoint(0, 0))
    
    def move_entity(self, x_shift: float, y_shift: float):
        self.coordinates.x += x_shift
        self.coordinates.y += y_shift
        
    def teleport_entity(self, x: float, y: float):
        self.coordinates.x = x
        self.coordinates.y = y

@dataclass
class World:
    _entities: list[Entity] = field(default_factory=lambda: list())
    
    def add_entity(self, entity: Entity):
        """
        Adds an entity to the World.

        :param entity: some object
        """
        self._entities.append(entity)
        
    def locate_entity(self, entity) -> WorldPoint | None:
        """
        Performs a reverse dictionary lookup.

        :param entity: an object to be looked up
        :return: the location of that object if it exists. None, otherwise.
        """
        for item in self._entities:
            if entity == item:
                return item.coordinates
        return None
        
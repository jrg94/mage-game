from dataclasses import dataclass

from .world import Entity


@dataclass
class Enemy(Entity):
    """
    The Enemy class represents enemy data.

    :param _hp: the health of the enemy
    """

    _hp: int = 10

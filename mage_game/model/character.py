from __future__ import annotations

from dataclasses import dataclass, field

from .magic import *


@dataclass
class PaletteItem:
    """
    Represents a single item in the game palette.

    :param Projectile spell: the spell that this item represents.
    :param float cooldown: the remaining time on the cooldown of the spell in milliseconds.
    """

    _spell: Projectile = field(default_factory=Projectile)
    _cooldown: float = 0

    def can_use(self) -> bool:
        """
        Returns True if the palette item is ready to be used.

        :return: True if the palette item is ready to be used.
        """
        return self._cooldown <= 0

    def reset_cooldown(self) -> None:
        """
        Resets the cooldown of the palette item.
        """
        self._cooldown = self._spell.get_attribute(SpellAttribute.COOLDOWN)

    def get_spell(self) -> Projectile:
        """
        Returns the spell of the palette item.

        :return: the spell of the palette item.
        """
        return self._spell
    
    def get_cooldown(self) -> float:
        return self._cooldown


@dataclass
class Palette:
    """
    Represents the game palette.

    :param list[PaletteItem] _items: the list of spells in the palette.
    :param int _current_spell_index: the index of the active spell in the palette.
    :param int _casting_time: the amount of time it takes to finish casting a spell in milliseconds
    """

    _items: list[PaletteItem] = field(default_factory=list)
    _current_item_index: int = 0
    _casting_time: int = 0

    def get_active_item(self) -> PaletteItem:
        """
        Retrieves the currently active spell from the palette.

        :return: the currently active spell.
        """
        return self._items[self._current_item_index]

    def get_active_item_index(self) -> int:
        """
        Retrieves the index of the currently active spell from the palette.

        :return: the index of the currently active spell.
        """
        return self._current_item_index

    def update_cooldowns(self, dt: float) -> None:
        """
        Lowers cooldowns for all spells in the palette.

        :param float dt: the time in milliseconds since the last update.
        """
        for palette_item in self._items:
            palette_item._cooldown -= dt
            if palette_item._cooldown <= 0:
                palette_item._cooldown = 0

    def can_cast_active_spell(self) -> bool:
        """
        Verifies that the currently active spell can be cast.

        :return: True if the spell can be cast, False otherwise.
        """
        return self.get_active_item().can_use() and self._casting_time <= 0

    def reset_active_spell_cooldown(self) -> None:
        """
        Resets the cooldown of the currently active spell.
        """
        self.get_active_item().reset_cooldown()

    def get_items(self) -> list[PaletteItem]:
        """
        Retrieves the list of spells in the palette.

        :return: the list of spells in the palette.
        """
        return self._items

    def set_active_palette_item(self, index: int) -> None:
        """
        Sets the currently active spell in the palette.

        :param index: the index of the spell in the palette.
        """
        self._current_item_index = index

    def reset_casting_time(self) -> None:
        """
        Sets the casting time to its effective value. Use when
        a spell is cast.
        """
        self._casting_time = self.get_active_item() \
            .get_spell() \
            .get_attribute(SpellAttribute.CAST_TIME) * 1000

    def update_casting_time(self, dt) -> None:
        """
        Takes some change in time and removes it from the current casting
        time. Forces casting time to zero if value drops below zero.

        :param dt: the change in time since the last time this method was called
        """
        self._casting_time -= dt
        if self._casting_time <= 0:
            self._casting_time = 0

    def get_remaining_casting_time(self) -> int:
        """
        Computes the remaining time spent casting a spell.

        :return: the time left to cast a spell in milliseconds
        """
        return self._casting_time
    
    def cast_active_spell(self) -> bool:
        """
        Attempts to cast the currently active spell.
        Returns True if the cast was successful.
        
        .. note::
           Casting does not actually do anything. It just manages
           the underlying state in an expected way (e.g., 
           checking if casting is possible, resetting cooldowns, etc.). 
           The view should handle the launching of the projectile. 
           
        :return: True if the cast was successful; False otherwise
        """
        if self.can_cast_active_spell():
            self.reset_active_spell_cooldown()
            self.reset_casting_time()
            return True
        return False

@dataclass
class Character:
    """
    The Character class represents the character data.

    :param spell_book: the list of spells that that the Character knows.
    :param Palette: a set of spells that the Character can use.
    """

    _spell_book: list[Projectile] = field(default_factory=list)
    _palette: Palette = field(default_factory=Palette)

    @staticmethod
    def new_character() -> Character:
        """
        Generates an instance of Character for new players.

        :return: an instance of Character populated with defaults.
        """
        character = Character()
        character._spell_book.extend([
            Projectile(Element.FIRE),
            Projectile(Element.WATER),
            Projectile(Element.EARTH),
            Projectile(Element.AIR),
            Projectile(Element.LIGHT),
            Projectile(Element.DARK),
        ])
        character._palette.get_items().extend([
            PaletteItem(spell) for spell in character._spell_book[:4]
        ])
        return character
    
    def cast(self) -> bool:
        """
        A convenience wrapper of the palette method cast_active_spell().
        May extend the functionality in the future to alter other character
        attributes. 
           
        :return: True if the cast was successful; False otherwise
        """
        return self._palette.cast_active_spell()
    
    def select_palette_item(self, selection: int) -> None:
        self._palette.set_active_palette_item(selection)

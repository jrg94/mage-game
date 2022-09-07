from magegame.model.character import Palette, PaletteItem
from magegame.model.magic import Element, Projectile, SpellAttribute


def test_palette_get_active_item_0():
    default = Palette()
    default.get_items().extend([
        PaletteItem()
    ])
    assert default.get_active_item_index() == 0
    assert default.get_active_item() == PaletteItem()
    
def test_palette_get_active_item_1():
    default = Palette()
    default.get_items().extend([
        PaletteItem(Projectile(Element.NONE)),
        PaletteItem(Projectile(Element.AIR))
    ])
    default.set_active_palette_item(1)
    assert default.get_active_item_index() == 1
    assert default.get_active_item() == PaletteItem(Projectile(Element.AIR))
    
def test_palette_can_cast_active_spell():
    default = Palette()
    default.get_items().extend([
        PaletteItem()
    ])
    assert default.can_cast_active_spell(), "The first spell should be able to be cast"
    
def test_cast_active_spell():
    default = Palette()
    default.get_items().extend([
        PaletteItem()
    ])
    default.cast_active_spell()
    assert not default.can_cast_active_spell(), "Active spell should be currently casting, so it cannot be cast again"
    assert default.get_active_item().get_cooldown() == SpellAttribute.COOLDOWN.base_value, "Active item should be on cooldown"
    assert default.get_active_item().get_spell().get_attribute(SpellAttribute.CAST_TIME) == SpellAttribute.CAST_TIME.base_value, "Active item should be casting"

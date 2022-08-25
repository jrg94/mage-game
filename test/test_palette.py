from mage_game.model.character import Palette, PaletteItem
from mage_game.model.magic import Element, Projectile


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
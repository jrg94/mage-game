from mage_game.model import *

def test_palette_item_default():
    default = PaletteItem()
    assert default.can_use() == True
    assert default.get_spell() == Projectile()
    
def test_palette_item_reset_cooldown():
    default = PaletteItem()
    default.reset_cooldown()
    assert default.get_cooldown() == SpellAttribute.COOLDOWN.base_value

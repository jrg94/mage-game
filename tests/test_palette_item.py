from mage_game.model import *

def test_palette_item_default():
    default = PaletteItem()
    assert default.can_use() == True, "Default palette items should be usable from the start"
    assert default.get_spell() == Projectile(), "Default palette items should store default projectiles"
    
def test_palette_item_reset_cooldown():
    default = PaletteItem()
    default.reset_cooldown()
    assert default.get_cooldown() == SpellAttribute.COOLDOWN.base_value, "Default palette items should store the default cooldown after reset"

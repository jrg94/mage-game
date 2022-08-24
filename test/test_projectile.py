from mage_game.model import Element, Projectile, SpellAttribute


def test_projectile_default():
    default = Projectile()
    assert default.element() == Element.NONE
    assert default.get_attribute(SpellAttribute.DAMAGE) == 1
from mage_game.model import Element, ProjectileSprite, SpellAttribute


def test_projectile_default():
    default = ProjectileSprite()
    assert default.element() == Element.NONE
    assert default.get_attribute(SpellAttribute.DAMAGE) == 1
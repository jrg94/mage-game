from magegame.model import *


def test_projectile_default():
    default = Projectile()
    assert default.element() == Element.NONE
    assert default.get_attribute(SpellAttribute.DAMAGE) == 1
    assert default.get_tracking(SpellAttribute.DAMAGE) == AttributeTracking(SpellAttribute.DAMAGE, _post=math.ceil, _units="hp")

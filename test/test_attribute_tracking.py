from mage_game import model

def test_tracking_default():
    tracking = model.AttributeTracking(model.SpellAttribute.DAMAGE, 10)
    assert tracking.effective_value() == 10

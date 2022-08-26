import math

from mage_game.model import AttributeTracking, SpellAttribute


def test_tracking_level_1():
    tracking = AttributeTracking(SpellAttribute.DISTANCE)
    assert tracking.level() == 1, "Default level should be 1"
    assert tracking.effective_value() == 10, "Provided distance should be 10: log2(1) * 10 + 10"
    assert tracking.events_to_next_level() == 10, "Default event count should be 10: ((2 ^ 2) - 2) * 5 - 0"


def test_tracking_level_2():
    tracking = AttributeTracking(SpellAttribute.DISTANCE)
    while tracking.level() != 2:
        tracking.trigger_event()
    assert tracking.level() == 2, "Tracker should have reached level 2"
    assert tracking.effective_value() == 20, "Computed value should be 20: log2(2) * 10 + 10"
    assert tracking.events_to_next_level() == 20, "Computed value should be 20: ((2 ^ 3) - 2) * 5 - 10"


def test_tracking_level_3():
    tracking = AttributeTracking(SpellAttribute.DISTANCE)
    while tracking.level() != 3:
        tracking.trigger_event()
    assert tracking.level() == 3, "Tracker should have reached level 3"
    assert math.ceil(tracking.effective_value()) == 26, "Computed value should be 25.84...: log2(3) * 10 + 10"
    assert tracking.events_to_next_level() == 40, "Computed value should be 40: ((2 ^ 4) - 2) * 5 - 30"

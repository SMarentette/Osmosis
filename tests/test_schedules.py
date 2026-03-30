import osmosis as osmo
from osmosis.base import OsmObject


def test_schedule_wrappers_use_base_getters_and_setters():
    model = osmo.Model.new()

    limits = model.add_schedule_type_limits("Fraction")
    limits.lower_limit_value = 0.0
    limits.upper_limit_value = 1.0
    limits.numeric_type = "Continuous"
    limits.unit_type = "Dimensionless"

    assert limits.lower_limit_value == 0.0
    assert limits.upper_limit_value == 1.0
    assert limits.numeric_type == "Continuous"
    assert limits.unit_type == "Dimensionless"

    constant = model.add_schedule_constant("Always On")
    constant.schedule_type_limits = limits
    constant.value = 1.0

    assert isinstance(constant.schedule_type_limits, OsmObject)
    assert constant.schedule_type_limits.handle == limits.handle
    assert constant.value == 1.0

    ruleset = model.add_schedule_ruleset("Office")
    ruleset.schedule_type_limits = limits

    assert isinstance(ruleset.default_day_schedule, OsmObject)
    assert ruleset.schedule_type_limits.handle == limits.handle

    rule = ruleset.add_rule("Weekdays")
    rule.apply_monday = True
    rule.apply_tuesday = True

    assert isinstance(rule.day_schedule, OsmObject)
    assert rule.apply_monday is True
    assert rule.apply_tuesday is True

    rule.day_schedule.schedule_type_limits = limits
    assert rule.day_schedule.schedule_type_limits.handle == limits.handle

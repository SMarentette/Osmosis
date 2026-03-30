from osmosis.base import OsmObject


class FakeOptional:
    def __init__(self, value):
        self._value = value

    def is_initialized(self):
        return self._value is not None

    def get(self):
        return self._value


class FakeSchedule:
    pass


FakeSchedule.__module__ = "openstudio.fake"


class FakeThermostat:
    def getHeatingSchedule(self):
        return FakeOptional(FakeSchedule())


def test_snake_case_can_resolve_get_camel_case_methods():
    thermostat = OsmObject(FakeThermostat())

    heating_schedule = thermostat.heating_schedule

    assert isinstance(heating_schedule, OsmObject)

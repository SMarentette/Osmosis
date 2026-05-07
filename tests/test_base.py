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


class FakeLowercaseConnector:
    def accountforDedicatedOutdoorAirSystem(self):
        return True

    def setAccountforDedicatedOutdoorAirSystem(self, value):
        self.value = value


def test_snake_case_preserves_lowercase_for_connector_word():
    obj = OsmObject(FakeLowercaseConnector())

    assert obj.account_for_dedicated_outdoor_air_system is True

    obj.account_for_dedicated_outdoor_air_system = False

    assert obj.raw.value is False


class FakeLowercaseAtConnector:
    def setpointatOutdoorLowTemperature(self):
        return 28

    def setSetpointatOutdoorLowTemperature(self, value):
        self.value = value


def test_snake_case_preserves_lowercase_at_connector_word():
    obj = OsmObject(FakeLowercaseAtConnector())

    assert obj.setpoint_at_outdoor_low_temperature == 28

    obj.setpoint_at_outdoor_low_temperature = 12

    assert obj.raw.value == 12


class FakeRemovable:
    def __init__(self):
        self.removed = False

    def remove(self):
        self.removed = True
        return ("removed",)


def test_remove_is_callable_wrapper_method():
    raw = FakeRemovable()
    obj = OsmObject(raw)

    result = obj.remove()

    assert raw.removed is True
    assert result == ("removed",)

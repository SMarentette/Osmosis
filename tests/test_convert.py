from osmosis import Convert


def test_flow_conversion_constants_and_helpers():
    assert Convert.M3_PER_SECOND_TO_CFM == 2118.88
    assert Convert.m3_per_second_to_cfm(1) == 2118.88
    assert round(Convert.cfm_to_m3_per_second(2118.88), 6) == 1


def test_temperature_conversion_helpers():
    assert Convert.c_to_f(0) == 32
    assert Convert.f_to_c(32) == 0


def test_power_per_flow_conversion_helpers():
    assert round(Convert.w_per_m3_per_second_to_w_per_cfm(2118.88), 6) == 1
    assert Convert.w_per_cfm_to_w_per_m3_per_second(1) == 2118.88

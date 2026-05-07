"""Common unit conversions for OpenStudio workflows."""


class Convert:
    M3_PER_SECOND_TO_CFM = 2118.88
    CFM_TO_M3_PER_SECOND = 1 / M3_PER_SECOND_TO_CFM
    W_PER_M3_PER_SECOND_TO_W_PER_CFM = 1 / M3_PER_SECOND_TO_CFM
    W_PER_CFM_TO_W_PER_M3_PER_SECOND = M3_PER_SECOND_TO_CFM

    M2_TO_FT2 = 10.7639
    FT2_TO_M2 = 1 / M2_TO_FT2

    M_TO_FT = 3.28084
    FT_TO_M = 1 / M_TO_FT

    W_TO_BTU_PER_HOUR = 3.41214
    BTU_PER_HOUR_TO_W = 1 / W_TO_BTU_PER_HOUR

    @staticmethod
    def m3_per_second_to_cfm(value: float) -> float:
        return value * Convert.M3_PER_SECOND_TO_CFM

    @staticmethod
    def cfm_to_m3_per_second(value: float) -> float:
        return value * Convert.CFM_TO_M3_PER_SECOND

    @staticmethod
    def w_per_m3_per_second_to_w_per_cfm(value: float) -> float:
        return value * Convert.W_PER_M3_PER_SECOND_TO_W_PER_CFM

    @staticmethod
    def w_per_cfm_to_w_per_m3_per_second(value: float) -> float:
        return value * Convert.W_PER_CFM_TO_W_PER_M3_PER_SECOND

    @staticmethod
    def c_to_f(value: float) -> float:
        return value * 9 / 5 + 32

    @staticmethod
    def f_to_c(value: float) -> float:
        return (value - 32) * 5 / 9

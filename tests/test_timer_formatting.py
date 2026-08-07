"""Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt."""
from styles import format_elapsed_time


def test_zero_seconds_is_zero_minutes():
    assert format_elapsed_time(0) == "0m"


def test_negative_seconds_clamped_to_zero():
    assert format_elapsed_time(-100) == "0m"


def test_under_a_minute_rounds_down_to_zero_minutes():
    assert format_elapsed_time(59) == "0m"


def test_exactly_one_minute():
    assert format_elapsed_time(60) == "1m"


def test_minutes_only_under_an_hour():
    assert format_elapsed_time(3599) == "59m"


def test_exactly_one_hour():
    assert format_elapsed_time(3600) == "1h 0m"


def test_hours_and_minutes_under_a_day():
    # 2h 30m = 9000s
    assert format_elapsed_time(9000) == "2h 30m"


def test_just_under_a_day_stays_in_hours():
    assert format_elapsed_time(86399) == "23h 59m"


def test_exactly_one_day():
    assert format_elapsed_time(86400) == "1d 0h"


def test_multi_day_value():
    # 2 días y 5 horas = 2*86400 + 5*3600 = 190800
    assert format_elapsed_time(190800) == "2d 5h"


def test_accepts_float_seconds():
    # datetime.timedelta.total_seconds() devuelve float; no debe reventar.
    assert format_elapsed_time(3600.75) == "1h 0m"

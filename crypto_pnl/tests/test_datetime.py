from crypto_pnl.core import (
    get_datetime,
    get_datetime_from_timestamp,
    format_datetime
)


def test_datetime_winter_time():
    a = get_datetime("2021-12-01 10:00:00")
    b = get_datetime_from_timestamp(int(1000*a.timestamp()))

    # Dublin is in UTC time zone
    assert format_datetime(a) == "2021-12-01 10:00:00"
    assert format_datetime(b) == "2021-12-01 10:00:00"


def test_datetime_summer_time():
    a = get_datetime("2021-06-01 10:00:00")
    b = get_datetime_from_timestamp(int(1000*a.timestamp()))

    # No daylight saving should be used
    assert format_datetime(a) == "2021-06-01 10:00:00"
    assert format_datetime(b) == "2021-06-01 10:00:00"

from datetime import datetime

from petshop.importer.utils import month_list, split_month


def test_split_month():
    # month with 31 days
    result = list(split_month(2024, 1, 3))
    assert result == [
        (datetime(2024, 1, 1), datetime(2024, 1, 10)),
        (datetime(2024, 1, 10), datetime(2024, 1, 20)),
        (datetime(2024, 1, 20), datetime(2024, 2, 1)),
    ]
    # month with 30 days
    result = list(split_month(2024, 4, 3))
    assert result == [
        (datetime(2024, 4, 1), datetime(2024, 4, 10)),
        (datetime(2024, 4, 10), datetime(2024, 4, 20)),
        (datetime(2024, 4, 20), datetime(2024, 5, 1)),
    ]
    # month with 29 days (2024 is a leap year)
    result = list(split_month(2024, 2, 3))
    assert result == [
        (datetime(2024, 2, 1), datetime(2024, 2, 9)),
        (datetime(2024, 2, 9), datetime(2024, 2, 19)),
        (datetime(2024, 2, 19), datetime(2024, 3, 1)),
    ]
    # month with 29 days (2023 is not a leap year)
    result = list(split_month(2023, 2, 3))
    assert result == [
        (datetime(2023, 2, 1), datetime(2023, 2, 9)),
        (datetime(2023, 2, 9), datetime(2023, 2, 18)),
        (datetime(2023, 2, 18), datetime(2023, 3, 1)),
    ]

    # split by 1
    result = list(split_month(2024, 1, 1))
    assert result == [
        (datetime(2024, 1, 1), datetime(2024, 2, 1)),
    ]
    # split by 4
    result = list(split_month(2024, 1, 4))
    assert result == [
        (datetime(2024, 1, 1), datetime(2024, 1, 7)),
        (datetime(2024, 1, 7), datetime(2024, 1, 15)),
        (datetime(2024, 1, 15), datetime(2024, 1, 23)),
        (datetime(2024, 1, 23), datetime(2024, 2, 1)),
    ]


def test_month_list_returns_list_of_first_of_month_dates():
    result = list(
        month_list(
            start=datetime(2023, 12, 1, 0, 0, 0), end=datetime(2024, 12, 5, 12, 34, 56)
        )
    )

    assert result == [
        datetime(2023, 12, 1, 0, 0, 0),
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 2, 1, 0, 0, 0),
        datetime(2024, 3, 1, 0, 0, 0),
        datetime(2024, 4, 1, 0, 0, 0),
        datetime(2024, 5, 1, 0, 0, 0),
        datetime(2024, 6, 1, 0, 0, 0),
        datetime(2024, 7, 1, 0, 0, 0),
        datetime(2024, 8, 1, 0, 0, 0),
        datetime(2024, 9, 1, 0, 0, 0),
        datetime(2024, 10, 1, 0, 0, 0),
        datetime(2024, 11, 1, 0, 0, 0),
        datetime(2024, 12, 1, 0, 0, 0),
    ]

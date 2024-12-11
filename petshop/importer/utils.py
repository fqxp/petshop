from calendar import monthrange
from collections.abc import Iterator
from datetime import date, datetime

from dateutil.relativedelta import relativedelta


def month_list(start: datetime, end: datetime) -> Iterator[date]:
    month = start
    while month < end:
        yield month
        month += relativedelta(months=1)


def split_month(
    year: int, month: int, number_of_splits: int
) -> Iterator[tuple[datetime, datetime]]:
    _, days_in_month = monthrange(year, month)
    days_per_split = days_in_month / number_of_splits
    end_of_month = datetime(year, month, 1) + relativedelta(months=1)

    for i in range(number_of_splits):
        start_day = datetime(year, month, int(i * days_per_split) or 1)
        end_day = (
            datetime(year, month, int((i + 1) * days_per_split))
            if i < number_of_splits - 1
            else end_of_month
        )

        yield (start_day, end_day)

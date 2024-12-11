import logging
import re
from datetime import datetime

import click
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from petshop.importer.import_downloads import get_incomplete_months, import_downloads
from petshop.importer.import_packages import import_packages


@click.group()
@click.option("-D", "--debug", is_flag=True, default=False, help="Enable debugging")
def cli(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    load_dotenv()  # pyright: ignore[reportUnusedCallResult]


@cli.add_command
@click.command()
def packages():
    import_packages()


# def validate_month(ctx: click.Context, param: str, month: str) -> datetime:
#     if not re.match(r"^\d\d\d\d-[12]\d$", month):
#         raise click.BadParameter("format must be 'YYYY-MM'")
#
#     return datetime.fromisoformat(f"{month}-01")


@cli.add_command
@click.command()
@click.argument("month_start", type=click.DateTime(formats=["%Y-%m"]))
@click.argument("month_end", type=click.DateTime(formats=["%Y-%m"]))
def downloads(month_start: datetime, month_end: datetime):
    """Import downloads for MONTH."""
    month = month_start
    while month <= month_end:
        import_downloads(month)
        month += relativedelta(months=1)


@cli.add_command
@click.command()
def validate_downloads():
    """Validate imported download counts."""
    incomplete_months = get_incomplete_months()

    if len(incomplete_months) == 0:
        print("🟢 found no incomplete months")
    else:
        print(
            "🔴 found the following incomplete months:"
            + ", ".join(m.isoformat() for m in incomplete_months)
        )

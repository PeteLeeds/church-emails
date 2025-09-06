import calendar
import datetime


def get_date_string(date: datetime) -> str:
    day = date.day
    month = calendar.month_name[date.month]
    year = date.year
    return f"{day} {month} {year}"

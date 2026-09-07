from datetime import datetime


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


def clean_text(value):
    """Normalize user-entered text for reliable searching and storage."""
    return " ".join(str(value).strip().split())


def normalize_id(value):
    return clean_text(value).upper()


def parse_date(date_text):
    date_text = clean_text(date_text)
    try:
        return datetime.strptime(date_text, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD format.") from exc


def parse_time(time_text):
    time_text = clean_text(time_text)
    try:
        return datetime.strptime(time_text, TIME_FORMAT).time()
    except ValueError as exc:
        raise ValueError("Time must use HH:MM format.") from exc


def valid_age(age):
    try:
        age = int(age)
    except (TypeError, ValueError):
        return False
    return 0 <= age <= 120


def valid_id(value, prefix):
    value = normalize_id(value)
    return bool(value) and value.startswith(prefix) and value[len(prefix):].isdigit()


def format_slot(doctor_id, date, time):
    """Return the required immutable appointment slot tuple."""
    return (normalize_id(doctor_id), str(date), clean_text(time))

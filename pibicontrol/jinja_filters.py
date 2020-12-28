from datetime import tzinfo, timedelta, datetime

def timestamp_to_date(value, format='%d-%m-%Y %H:%M'):
  if value:
    return datetime.fromtimestamp(int(value)).strftime(format)
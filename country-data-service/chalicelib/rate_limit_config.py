from datetime import timedelta

RATE_LIMITS = {
    'fetch_country_data': {'limit': 200, 'period': timedelta(minutes=1)},
    'get_country_data': {'limit': 200, 'period': timedelta(minutes=1)},
    'check_operation_status': {'limit': 300, 'period': timedelta(minutes=1)}
}

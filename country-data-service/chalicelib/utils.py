from functools import wraps
from chalice import BadRequestError
from decimal import Decimal
import json

def validate_country(country_service):
    def decorator(f):
        @wraps(f)
        def wrapper(country, *args, **kwargs):
            if not country_service.validate_country_name(country):
                raise BadRequestError("Invalid country name. It should be more than 3 letters and only contain letters and hyphens.")
            return f(country, *args, **kwargs)
        return wrapper
    return decorator

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

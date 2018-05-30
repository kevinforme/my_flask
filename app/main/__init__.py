from functools import wraps

from flask import Blueprint, request
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()


def cached(timeout=60 * 5, prefix='view/%s'):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            cache_key = prefix % request.path
            value = cache.get(cache_key)
            if value is None:
                value = f(*args, **kwargs)
                cache.set(cache_key, value, timeout=timeout)
            return value
        return wrap
    return decorator


main = Blueprint('main', __name__)

from . import views

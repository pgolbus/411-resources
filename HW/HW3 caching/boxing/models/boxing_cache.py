import time
from boxing.models import Boxers

_boxer_cache = {}
_ttl = {}
ttl_seconds = 60  # You can customize this value

def get_boxer_cached(boxer_id: int) -> Boxers:
    """Get a boxer from cache or database, refreshing TTL if needed."""
    now = time.time()

    if boxer_id in _boxer_cache and _ttl[boxer_id] > now:
        return _boxer_cache[boxer_id]

    boxer = Boxers.get_boxer_by_id(boxer_id)
    _boxer_cache[boxer_id] = boxer
    _ttl[boxer_id] = now + ttl_seconds
    return boxer

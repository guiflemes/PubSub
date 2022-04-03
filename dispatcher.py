from functools import wraps
from typing import Callable, Set
from publisher import Publisher


def dispatch_events(events: Set[str]) -> Callable:
    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            result = func(*args, **kwargs)

            for event in events:
                Publisher().dispatch(event, result)

            return result

        return wrapper

    return _decorator

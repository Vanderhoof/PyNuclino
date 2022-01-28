import time
from functools import wraps
from ratelimit.exception import RateLimitException


def sleep_and_retry(quiet: bool = False):
    def decorator(func):
        '''
        This is sleep_and_retry decorator from ratelimit library but with added
        printed message so that user is aware of the delay.
        '''

        @wraps(func)
        def wrapper(*args, **kargs):
            while True:
                try:
                    return func(*args, **kargs)
                except RateLimitException as exception:
                    if not quiet:
                        print(f'Rate limited. Sleeping for {exception.period_remaining:.0f} seconds')
                    time.sleep(exception.period_remaining)
        return wrapper
    return decorator

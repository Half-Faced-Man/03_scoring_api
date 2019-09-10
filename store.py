import time
#import tarantool
import functools
import redis


# def reconnect(cases):
#     def decorator(f):
#         @functools.wraps(f)
#         def wrapper(*args):
#             for c in cases:
#                 new_args = args + (c if isinstance(c, tuple) else (c,))
#                 f(*new_args)
#         return wrapper
#     return decorator


def reconnect(max_connections, connect_timeout):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in range(max_connections):
                try:
                    return f(*args)
                except (TimeoutError, ConnectionError):
                    print('connect {}'.format(c))
                    time.sleep(connect_timeout)
            #f(*args)
        return wrapper
    return decorator


class RedisStore:

    def __init__(self, port=6379, host='localhost'):
        self.port = port
        self.host = host
        self.connection = None
        self.create_connection()

    def create_connection(self):
        self.connection = redis.StrictRedis(host=self.host, port=self.port)

    def set(self, key, val, ex):
        try:
            return self.connection.set(key, val, ex)
        except redis.exceptions.ConnectionError:
            raise ConnectionError
        except redis.exceptions.TimeoutError:
            raise TimeoutError

    def get(self, key):
        try:
            return self.connection.get(key)
        except redis.exceptions.ConnectionError:
            raise ConnectionError
        except redis.exceptions.TimeoutError:
            raise TimeoutError


class Store:

    def __init__(self):
        self.kvstore = RedisStore()

    # эти функцции должны долбиться и на них надо проверять реконнеки
    @reconnect(max_connections=5, connect_timeout=5)
    def set(self, key, val, ex=None):
        return self.kvstore.set(key, val, ex)

    @reconnect(max_connections=5, connect_timeout=5)
    def get(self, key):
        return self.kvstore.get(key)

    # эти функции не переподдючаются, подразумевается что кэш есть в доступе всегда . тест на реконнект не нужно делать
    def cache_set(self, key, val, ex=None):
        return self.kvstore.set(key, val, ex)

    def cache_get(self, key):
        return self.kvstore.get(key)


# side_effect side_effect side_effect side_effect side_effect side_effect side_effect side_effect
import json

try:
    import redis
except ImportError:
    imported_redis = None

__all__ = ['storage']


def storage(storage_config, index):
    if 'dict' in storage_config:
        return InMemoryStorage(storage_config)
    elif 'redis' in storage_config:
        storage_config['db'] = index
        return RedisStorage(storage_config)
    else:
        raise ValueError("Only in-memory dictionary and Redis and supported.")


class BaseStorage(object):
    def __init__(self, config):
        raise NotImplementedError

    def keys(self):
        """ Returns a list of binary hashes """
        raise NotImplementedError

    def set_val(self, key, val):
        raise NotImplementedError

    def get_val(self, key):
        raise NotImplementedError

    def append_val(self, key, val):
        raise NotImplementedError

    def get_list(self, key):
        raise NotImplementedError


class InMemoryStorage(BaseStorage):
    def __init__(self, config):
        self.name = 'dict'
        self.storage = dict()

    def keys(self):
        self.storage.keys()

    def set_val(self, key, val):
        self.storage[key] = val

    def get_val(self, key):
        return self.storage[key]

    def append_val(self, key, val):
        self.storage.setdefault(key, []).append(val)

    def get_list(self, key):
        return self.storage.get(key, [])


class RedisStorage(BaseStorage):
    def __init__(self, config):
        if not imported_redis:
            raise ImportError("redis-py is required to use Redis as storage.")
        self.name = 'redis'
        try:
            self.storage = redis.StrictRedis(**config)
        except Exception:
            print("ConecctionError occur when trying to connect to redis.")
            raise

    def keys(self, pattern="*"):
        self.storage.keys(pattern)

    def set_val(self, key, val):
        self.storage.set(key, val)

    def get_val(self, key):
        return self.storage.get(key)

    def append_val(self, key, val):
        self.storage.rpush(key, json.dumps(val))

    def get_list(self, key):
        return self.storage.lrange(key, 0, -1)

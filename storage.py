import json

try:
    import redis
except ImportError:
    imported_redis = None

__all__ = ['InMemoryStorage', 'RedisStorage']


class BaseStorage(object):
    def __init__(self, name):
        raise NotImplementedError

    def keys(self):
        """ Returns a list of binary hashes """
        raise NotImplementedError

    def set_val(self, key, value):
        raise NotImplementedError

    def get_val(self, key):
        raise NotImplementedError

    def append_val(self, key, value):
        raise NotImplementedError

    def get_list(self, key):
        raise NotImplementedError


class InMemoryStorage(BaseStorage):
    def __init__(self, name):
        self.name = 'dict'
        self.storage = dict()

    def keys(self):
        self.storage.keys()

    def set_val(self, key, value):
        self.storage[key] = value

    def get_val(self, key):
        return self.storage[key]

    def append_val(self, key, value):
        try:
            self.storage[key].append(value)
        except KeyError:
            self.storage[key] = list(value)

    def get_list(self, key):
        return self.storage[key]


class RedisStorage(BaseStorage):
    def __init__(self, name, config):
        if not imported_redis:
            raise ImportError("Redis is required for using Redis as storage")
        self.name = 'redis'
        self.storage = redis.StrictRedis(config)

    def keys(self, pattern="*"):
        self.storage.keys(pattern)

    def set_val(self, key, val):
        self.storage.set(key, val)

    def get_val(self, key):
        return self.storage.get(key)

    def append_val(self, key, val):
        if isinstance(val, basestring):
            self.storage.rpush(key, val)
        else:
            self.storage.rpush(key, json.dumps(val))

    def get_list(self, key):
        return self.storage.lrange(key, 0, -1)

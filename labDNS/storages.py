try:
    import redis
except ImportError:
    redis = None


class BaseStorage:
    DEFAULT_CONFIG = dict()

    def __init__(self, config):
        self.config = self.DEFAULT_CONFIG
        self._configure(config)

    def get(self, key):
        raise NotImplementedError

    def _configure(self, config):
        self.config.update(config)


class DictStorage(BaseStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dictionary = self.config

    def get(self, key, default=None):
        return self.dictionary.get(key, default)


class RedisStorage(BaseStorage):
    DEFAULT_SETTINGS = dict(host='localhost', port=6379, db=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = redis.StrictRedis(**self.config)

    def get(self, key, default=None):
        return self.redis.get(key).decode("utf-8") or default

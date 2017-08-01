try:
    import redis
except ImportError:
    redis = None
try:
    import consul
except ImportError:
    consul = None


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
        value = self.redis.get(key)
        return value.decode("utf-8") if value else default


class ConsulStorage(BaseStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consul = consul.Consul(**self.config)

    def _configure(self, config):
        self.key_prefix = config.pop('key_prefix', None)
        self.config.update(config)

    def get(self, key, default=None):
        index, data = self.consul.kv.get(self.key_prefix + key)
        value = data['Value'] if data else None
        return value.decode("utf-8") if value else default

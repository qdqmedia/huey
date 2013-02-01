from huey.backends.base import BaseQueue, BaseDataStore
from huey.utils import EmptyData
from huey.djhuey.models import BackgroundTask, BackgroundResultTask


class PostgresQueue(BaseQueue):
    """
    A simple Queue that uses PostgreSQL to store messages
    """
    def __init__(self, name, **connection):
        super(PostgresQueue, self).__init__(name, **connection)

        self.queue_name = name

    def write(self, data):
        BackgroundTask.objects.create(data=data, name=self.queue_name)

    def read(self):
        try:
            task = BackgroundTask.objects.select_for_update().filter(processing=False).order_by('pk')[0]
            task.processing = True
            task.save()
        except IndexError:
            return None
        data = task.data
        task.delete()
        return data

    def remove(self, data):
        try:
            task = BackgroundTask.objects.get(data=data)
            data = task.data
            task.delete()
            return data
        except BackgroundTask.DoesNotExist:
            return ''

    def flush(self):
        BackgroundTask.objects.filter(self.queue_name).delete()

    def __len__(self):
        return BackgroundTask.objects.all().count()


class RedisDataStore(BaseDataStore):
    def __init__(self, name, **connection):
        """
        RESULT_STORE_CONNECTION = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        }
        """
        super(RedisDataStore, self).__init__(name, **connection)

        self.storage_name = 'huey.redis.results.%s' % re.sub('[^a-z0-9]', '', name)
        self.conn = redis.Redis(**connection)

    def put(self, key, value):
        self.conn.hset(self.storage_name, key, value)

    def peek(self, key):
        if self.conn.hexists(self.storage_name, key):
            return self.conn.hget(self.storage_name, key)
        return EmptyData

    def get(self, key):
        val = self.peek(key)
        if val is not EmptyData:
            self.conn.hdel(self.storage_name, key)
        return val

    def flush(self):
        self.conn.delete(self.storage_name)

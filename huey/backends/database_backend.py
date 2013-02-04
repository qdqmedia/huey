import pickle

from django.conf import settings

from huey.backends.base import BaseQueue, BaseDataStore
from huey.utils import EmptyData
from huey.djhuey.models import BackgroundTask, BackgroundResultTask


class DatabaseQueue(BaseQueue):
    """
    A simple Queue that uses a database to store messages

    Don't forget to add following property to your Django settings file:

    HUEY_CONFIG = {'QUEUE': 'huey.backends.database_backend.DatabaseQueue',}

    Task stored in table won't be deleted. If you want to do that, you should
    add next line to your 'settings.py' file:

    HUEY_DATABASE_BACKEND_DELETE_TASK = True
    """
    def __init__(self, name, **connection):
        super(DatabaseQueue, self).__init__(name, **connection)

        self.queue_name = name

    def write(self, data):
        key = pickle.loads(data)[0]
        BackgroundTask.objects.create(data=data, name=self.queue_name, key=key)

    def read(self):
        try:
            task = BackgroundTask.objects.select_for_update().filter(processing=False).order_by('pk')[0]
            task.processing = True
            task.save()
        except IndexError:
            return None
        data = task.data
        del_task = getattr(settings, 'HUEY_DATABASE_BACKEND_DELETE_TASK', False)
        if del_task:
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


class DatabaseDataStore(BaseDataStore):
    def __init__(self, name, **connection):
        super(DatabaseDataStore, self).__init__(name, **connection)

        self.storage_name = name

    def put(self, key, value):
        BackgroundResultTask.objects.create(name=self.storage_name, key_id=key, result=value)

    def peek(self, key):
        try:
            return BackgroundResultTask.objects.get(name=self.storage_name, key_id=key).result
        except BackgroundResultTask.DoesNotExist:
            return EmptyData

    def get(self, key):
        val = self.peek(key)
        if val is not EmptyData:
            BackgroundResultTask.objects.get(name=self.storage_name, key_id=key).delete()
        return val

    def flush(self):
        BackgroundResultTask.objects.filter(self.queue_name).delete()

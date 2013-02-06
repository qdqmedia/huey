import pickle

from django.db import transaction
from django.utils.decorators import method_decorator

from huey.backends.base import BaseQueue, BaseDataStore
from huey.utils import EmptyData
from huey.djhuey.models import BackgroundTask, BackgroundResultTask


class DjangoDBQueue(BaseQueue):
    """
    A simple Queue that uses a database to store messages

    Configuration example:

    HUEY_CONFIG = {
        'QUEUE': 'huey.backends.database_backend.DjangoDBQueue',
        'RESULT_STORE': 'huey.backends.django_db_backend.DjangoDBDataStore',
    }

    """
    def __init__(self, name, **connection):
        super(DjangoDBQueue, self).__init__(name, **connection)

        self.queue_name = name

    @method_decorator(transaction.commit_manually)
    def write(self, data):
        key = pickle.loads(data)[0]

        if BackgroundTask.objects.filter(name=self.queue_name, key=key).count() == 0:
            BackgroundTask.objects.create(data=data, name=self.queue_name, key=key)
        else:
            task = BackgroundTask.objects.select_for_update().get(key=key)
            task.processing = False
            task.save()

        transaction.commit()

    @method_decorator(transaction.commit_manually)
    def read(self):
        try:
            task = BackgroundTask.objects.select_for_update().filter(processing=False, name=self.queue_name).order_by('pk')[0]
            task.processing = True
            task.save()
            transaction.commit()
        except IndexError:
            transaction.rollback()
            return None

        return task.data

    def remove(self, data):
        try:
            task = BackgroundTask.objects.get(data=data)
            data = task.data
            task.delete()
            return data
        except BackgroundTask.DoesNotExist:
            return ''

    def flush(self):
        BackgroundTask.objects.filter(name=self.queue_name).delete()

    def __len__(self):
        return BackgroundTask.objects.all().count()


class DjangoDBDataStore(BaseDataStore):
    def __init__(self, name, **connection):
        super(DjangoDBDataStore, self).__init__(name, **connection)

        self.storage_name = name

    def put(self, key, value):
        BackgroundResultTask.objects.create(name=self.storage_name, key_id=key, result=value)

    def peek(self, key):
        try:
            result = BackgroundResultTask.objects.get(name=self.storage_name, key_id=key).result
            return result
        except BackgroundResultTask.DoesNotExist:
            return EmptyData

    def get(self, key):
        val = self.peek(key)
        if val is not EmptyData:
            BackgroundResultTask.objects.get(name=self.storage_name, key_id=key).delete()
        return val

    def flush(self):
        BackgroundResultTask.objects.filter(name=self.storage_name).delete()

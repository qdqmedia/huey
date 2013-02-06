import pickle

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BackgroundTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Queue name'))
    data = models.TextField()
    processing = models.BooleanField(default=False)
    key = models.CharField(max_length=255, verbose_name=_(u'Command'), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def task_name(self):
        try:
            return pickle.loads(self.data)[1]
        except:
            return None

    def __unicode__(self):
        return unicode('{0} - {1}'.format(self.name, self.key))


class BackgroundResultTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Queue name'))
    result = models.TextField()
    key = models.ForeignKey(BackgroundTask, to_field='key')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def task_result(self):
        try:
            return pickle.loads(self.result)
        except:
            return None

    def __unicode__(self):
        return unicode('{0} - {1}'.format(self.name, self.key))

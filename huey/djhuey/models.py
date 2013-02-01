from django.db import models
from django.utils.translation import ugettext_lazy as _


class BackgroundTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Queue name'))
    data = models.TextField()
    processing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class BackgroundResultTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Queue name'))
    result = models.TextField()
    key = models.CharField(max_length=255, verbose_name=_(u'key'))
    created_at = models.DateTimeField(auto_now_add=True)

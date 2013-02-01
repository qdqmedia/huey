from django.db import models
from django.utils.translation import ugettext_lazy as _


class BackgroundTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'key name'))
    data = models.TextField()
    processing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class BackgroundResultTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'key name'))
    result = models.CharField(max_length=255, verbose_name=_(u'result'))
    created_at = models.DateTimeField(auto_now_add=True)

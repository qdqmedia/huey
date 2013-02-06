from django.conf.urls.defaults import url, patterns

from huey.djhuey import views


urlpatterns = patterns('huey.djhuey.views',
    url(r'^$', views.BackgroundTasksList.as_view(), name='djhuey-home'),
)

from django.views.generic import ListView

from .models import BackgroundTask


class BackgroundTasksList(ListView):
    paginate_by = 15

    def get_queryset(self):
        return BackgroundTask.objects.all().order_by('-id')

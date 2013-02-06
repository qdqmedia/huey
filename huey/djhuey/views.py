from django.views.generic import ListView

from .models import BackgroundTask

class BackgroundTasksList(ListView):
    paginate_by = 50
    model = BackgroundTask
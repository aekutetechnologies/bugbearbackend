from django.urls import path
from .views import CreateInstanceView, StopInstanceView, DeleteInstanceView

urlpatterns = [
    path('create/', CreateInstanceView.as_view(), name='create_instance'),
    path('stop/', StopInstanceView.as_view(), name='stop_instance'),
    path('delete/', DeleteInstanceView.as_view(), name='delete_instance'),
]

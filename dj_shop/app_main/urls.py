from django.urls import path
from .views import Index


app_name = 'app_main'

urlpatterns = [
    path('', Index.as_view(), name='index'),
]

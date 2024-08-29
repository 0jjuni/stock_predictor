from django.urls import path
from .views import home, model_performance

urlpatterns = [
    path('', home, name='home'),  # 루트 URL
    path('model-performance/', model_performance, name='model_performance'),
]

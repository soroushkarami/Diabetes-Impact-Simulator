from django.urls import path
from .views import predict_view, simulate_view

urlpatterns = [
    path('', predict_view, name='diabetes_predictor'),
    path('simulate/', simulate_view, name='diabetes_simulator')
]
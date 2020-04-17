from django.urls import path

from .views import celebrities

urlpatterns = [
	path("", celebrities, name = "celebrities")
]
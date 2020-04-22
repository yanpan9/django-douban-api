from django.urls import path

from .views import episodes

urlpatterns = [
	path("", episodes, name = "episodes")
]
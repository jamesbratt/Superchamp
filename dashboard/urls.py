from django.conf.urls import url
from .views import DashboardHomeView

urlpatterns = [
    url(r'^$', DashboardHomeView.as_view(), name='dashboard'),
]

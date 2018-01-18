from django.conf.urls import url

from .views import UploadView, TimeStats

urlpatterns = [
    url(r'^upload/$', UploadView.as_view(), name='upload-data'),
    url(r'^ajax-time-stats/(?P<pk>[-\w]+)/$', TimeStats.as_view(), name='time-stats'),
]
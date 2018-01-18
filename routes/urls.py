from django.conf.urls import url

from .views import CreateRouteView, CreateRouteAjax, CreateRouteSuccess, DetailRouteView, ListRouteView, GetRouteCoordinates, RouteGPXDownload

urlpatterns = [
    url(r'^create/$', CreateRouteView.as_view(), name='create-route'),
    url(r'^ajax-create/$', CreateRouteAjax.as_view(), name='ajax-route'),
    url(r'^(?P<pk>[-\w]+)/$', DetailRouteView.as_view(), name='route-detail'),
    url(r'^(?P<pk>[-\w]+)/download-gpx/$', RouteGPXDownload.as_view(), name='download-stage'),
    url(r'^create/success/(?P<pk>[-\w]+)/$', CreateRouteSuccess.as_view(), name='create-success'),
    url(r'^coordinates/(?P<pk>[-\w]+)/$', GetRouteCoordinates.as_view(), name='create-success'),
    url(r'^$', ListRouteView.as_view(), name='list-routes'),
]
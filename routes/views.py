import json
import gpxpy.gpx
import time
import datetime

from django.db.models import Min

from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages

from django.http import HttpResponse, Http404, JsonResponse

from polyline.codec import PolylineCodec

from challenges.models import ChallengeTime

from .forms import CreateRouteForm
from .models import Route


class CreateRouteView(LoginRequiredMixin, FormView):
    login_url = '/account/login/'
    template_name = 'routes/route_create.html'
    form_class = CreateRouteForm


class CreateRouteSuccess(LoginRequiredMixin, TemplateView):
    login_url = '/account/login/'
    template_name = 'routes/route_create_success.html'

    def dispatch(self, request, *args, **kwargs):
        if not Route.objects.filter(pk=self.kwargs['pk']).exists():
            raise Http404

        return super(CreateRouteSuccess, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateRouteSuccess, self).get_context_data(**kwargs)
        context['route_id'] = self.kwargs['pk']
        return context


class DetailRouteView(DetailView):
    model = Route
    template_name = 'routes/route_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(DetailRouteView, self).get_context_data(**kwargs)
            
        efforts = ChallengeTime.objects.filter(route=self.object.id).order_by('created_date')

        context['times'] = efforts
        latest_effort = ChallengeTime.objects.filter(route=self.object.id)
        if latest_effort:
            context['latest_effort'] = latest_effort.latest('created_date')

        return context


class ListRouteView(ListView):
    model = Route
    template_name = 'routes/route_list.html'
    
    
class RouteGPXDownload(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def get(self, request, **kwargs):
        route = Route.objects.get(pk=kwargs['pk'])
        polyLine = route.polyline
        DecodedStage = PolylineCodec().decode(polyLine)

        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for position in DecodedStage:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(position[0], position[1], elevation=0))

        fileName = route.title
        fileName2 = fileName.replace(" ", "")

        response = HttpResponse(gpx.to_xml(), content_type='text/xml')
        response['Content-Disposition'] = 'attachment; filename="'+fileName2+'.gpx"'

        return response


class GetRouteCoordinates(View):
    def get(self, request, **kwargs):
        if request.is_ajax():
            routeID = self.kwargs['pk']
            route = Route.objects.filter(pk=routeID).values()[0]

            polyLine = route['polyline']
            DecodedRace = PolylineCodec().decode(polyLine)
            coordList = []
            for location in DecodedRace:
                obj = {'lat': location[0], 'lng': location[1]}
                coordList.append(obj)
            jsonObj = json.dumps(coordList)

            return JsonResponse(jsonObj, safe=False)


class CreateRouteAjax(View, LoginRequiredMixin):
    def post(self, request):
        if request.is_ajax():
            data = {
                'title': request.POST.get("title", ""),
                'difficulty': request.POST.get("difficulty", ""),
                'country': request.POST.get("country", ""),
                'locality': request.POST.get("locality", ""),
                'polyline': request.POST.get("polyline", ""),
                'distance': request.POST.get("distance", ""),
                'start_lat': request.POST.get("start_lat", ""),
                'start_long': request.POST.get("start_long", ""),
                'finish_lat': request.POST.get("finish_lat", ""),
                'finish_long': request.POST.get("finish_long", ""),
                'min_elevation': request.POST.get("min_elevation", ""),
                'max_elevation': request.POST.get("max_elevation", ""),
                'elevation_gain': request.POST.get("elevation_gain", "")
            }

            form = CreateRouteForm(data)
            if form.is_valid():
                user = User.objects.get(pk=request.user.id)
                form.cleaned_data['user'] = user
                form.cleaned_data['created_date'] = datetime.date.today()
                distanceMeters = form.cleaned_data['distance']
                distanceKm = distanceMeters / 1000
                del form.cleaned_data['distance']
                form.cleaned_data['distance'] = distanceKm
                route = Route(**form.cleaned_data)
                route.save()

                response = HttpResponse(route.id, content_type='application/json')
                response.status_code = 200
                return response

            else:
                response = HttpResponse(form.errors.as_json(), content_type='application/json')
                response.status_code = 400
                return response

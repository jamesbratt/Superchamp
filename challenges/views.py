import datetime
import time
import json
import operator

from django.shortcuts import render
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic.edit import FormView
from django.views.generic import View

from .models import ChallengeTime
from .forms import UploadTimeForm
from .fitFileValidator import AnalytseFile

from django.contrib.gis.geos import Point


class TimeStats(View):
    
    def distance(self, point, ref):
        p = Point((point['longitude'], point['latitude']), srid=4326)
        dist = p.distance(Point((ref['longitude'], ref['latitude']), srid=4326))
        resp = (point['longitude'], dist, point['latitude'], point['elevation'], point['time'], point['speed'])
        return resp

    def get(self, request, **kwargs):
        if request.is_ajax():
            challengeTimeId = request.GET.get('challengeTimeId', '')
            payload = None
            
            latest = ChallengeTime.objects.filter(route=self.kwargs['pk']).latest('created_date')
            data = ChallengeTime.objects.get(pk=challengeTimeId)
            
            new_data = []
            
            for points in json.loads(latest.data):
                match_positions = [self.distance(position, points) for position in json.loads(data.data)]
                sortedList = sorted(match_positions, key=operator.itemgetter(1))
                obj = {'latitude':sortedList[0][2], 'longitude':sortedList[0][0], 'elevation':sortedList[0][3], 'time':sortedList[0][4], 'speed':sortedList[0][5]}
                new_data.append(obj)
            payload = {'id': data.id, 'label': data.user.username + ' ' + data.created_date.strftime('%Y-%m-%d %H:%M:%S'), 'data': json.dumps(new_data)}
                
            return JsonResponse(payload, safe=False)


class UploadView(LoginRequiredMixin, FormView):
    login_url = '/account/login/'
    template_name = 'challenges/upload_data.html'
    form_class = UploadTimeForm
    success_url = '/challenges/upload'

    def process_challenges(self, upload, route):
        user = User.objects.get(pk=self.request.user.pk)

        uploaded_time = upload['duration'].total_seconds()

        # Calculate performance
        performance = 0
        if ChallengeTime.objects.filter(user=self.request.user.pk).filter(route=route.id).exists():
            previous_effort = ChallengeTime.objects.filter(user=self.request.user.pk).filter(route=route.id).latest('created_date')

            if previous_effort is not None:
                diff = 0
                previous_time = previous_effort.duration
                if previous_time > uploaded_time:
                    diff = previous_time - uploaded_time
                elif previous_time < uploaded_time:
                    neg_diff = uploaded_time - previous_time
                    if neg_diff > 0:
                        diff = -neg_diff

                if diff is not None:
                    performance = round(100 * float(diff)/float(previous_time), 1)

        ChallengeTime.objects.create(
            user=user,
            route=route,
            duration=uploaded_time,
            duration_str=time.strftime('%H:%M:%S', time.gmtime(uploaded_time)),
            average_speed=upload['average_speed'],
            created_date=datetime.datetime.now(),
            start_time=upload['start_time'],
            performance=performance,
            data=upload['data']
        )
        
        return {'duration': time.strftime('%H:%M:%S', time.gmtime(uploaded_time)), 'route_id': route.id, 'performance': performance, 'user': user, 'average_speed': upload['average_speed']}

    def form_valid(self, form):
        route = form.cleaned_data['route']
        fit_file = form.cleaned_data['fitFile']
        data = fit_file.read()
        validateTime = AnalytseFile().Validate(data, route.id)

        if validateTime is False:
            messages.add_message(self.request, messages.ERROR, 'Invalid route taken!')
        elif validateTime == 'reverse':
            messages.add_message(self.request, messages.ERROR, 'Route error! You may have ridden the route the wrong way round.')
        else:
            results = self.process_challenges(validateTime, route)
            messages.add_message(self.request, messages.INFO, 'Your ride has been successfully uploaded.')

            return render(self.request, 'challenges/challenge_upload_success.html', {'results': results})

        return super(UploadView, self).form_valid(form)

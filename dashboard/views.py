import json

from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse

from django.views.generic import TemplateView
from django.views.generic import View


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = '/account/login/'

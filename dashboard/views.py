from django.views.generic import TemplateView


class DashboardHomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            self.template_name = 'dashboard/home.html'

        return super(DashboardHomeView, self).dispatch(request, *args, **kwargs)

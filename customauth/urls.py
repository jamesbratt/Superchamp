from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from .views import Register, Activate, Account

urlpatterns = [
    url(r'^login/', auth_views.login, {'template_name': 'customauth/login.html', 'authentication_form': LoginForm, 'extra_context':{'metaTitle':'Sign In | Superchamp','metaDescription':'Sign in to Superchamp and start participating in and organising local cycling events.'}}, name='login'),
    url(r'^logout/', auth_views.logout_then_login, {'login_url': '/account/login/'}, name='logout'),
    # url(r'^register/', Register.as_view(), name='register'),
    # url(r'^activate/(?P<key>.+)$', Activate.as_view(), name='account-activation'),
    # url(r'^(?P<pk>[-\w]+)/$', Account.as_view(), name='user-account'),
]

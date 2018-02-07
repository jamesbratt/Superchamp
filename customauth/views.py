from django.http import HttpResponseRedirect
from django.http import Http404
from .forms import RegisterForm, AccountForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.contrib.auth.models import User
from .models import Profile
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone


class Register(CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/account/login/'
    template_name = 'customauth/register.html'

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        context['metaTitle'] = 'Register | Superchamp'
        context['metaDescription'] = 'Register with Superchamp and start participating in and organising cycling events in your local area.'
        return context

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'You are almost there! We have sent you an email just to verify your account. Please check your emails, including your junk mail folder.')
        return 'customauth/register.html'

    def get_form_kwargs( self ):
        kwargs = super( Register, self ).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class Account(UpdateView):
    model = User
    template_name = "customauth/account.html"
    form_class = AccountForm

    def get_context_data(self, **kwargs):
        context = super(Account, self).get_context_data(**kwargs)
        context['metaTitle'] = 'Your Account | Superchamp'
        context['metaDescription'] = ''
        return context

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'Your account details have been updated!')
        return '/account/' + str(self.object.id) + '/'

    def dispatch(self, request, *args, **kwargs):
        if str(request.user.id) != str(kwargs['pk']):
            raise Http404

        return super(Account, self).dispatch(request, *args, **kwargs)


class Activate(TemplateView):
    template_name = "customauth/activate.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            raise Http404

        return super(Activate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Activate, self).get_context_data(**kwargs)
        profile = get_object_or_404(Profile, activation_key=kwargs['key'])
        context['metaTitle'] = 'Your Account | Superchamp'
        context['metaDescription'] = ''

        if profile.user.is_active == False:
            if timezone.now() > profile.key_expires:
                messages.add_message(self.request, messages.ERROR, 'Your activation has expired, please register again.')
            else:
                profile.user.is_active = True
                profile.user.save()
                messages.add_message(self.request, messages.INFO, 'Your account has been successfully activated. You can now <a href="/account/login/">sign in</a>!')

        else:
            messages.add_message(self.request, messages.ERROR, 'This account has already been activated. Go ahead and <a href="/account/login/">sign in</a>!')
        return context

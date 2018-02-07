import datetime
import hashlib

from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Profile


class RegisterForm(UserCreationForm):
    request = None
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required':'true', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required':'true', 'data-match':'#id_password1', 'placeholder': 'Confirm Password'}),
        strip=False,
        help_text=("Enter the same password as before, for verification."),
    )
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required':'true', 'placeholder': 'Email Address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'required':'true', 'placeholder': 'Username'}),
        }

    def __init__( self, request, *args, **kwargs ):
        self.request = request
        super( RegisterForm, self ).__init__(*args, **kwargs )

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        if commit:
            user.is_active = False
            user.save()

            expiry = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
            key = self.generate_activation_key(user.username)
            Profile.objects.create(user = user,
                                   activation_key = key,
                                   key_expires = expiry
                                   )

            self.sendEmail(key, user.email, user.username)

        return user

    def sendEmail(self, key, email, username):

        if self.request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        url =  protocol + self.request.META['HTTP_HOST'] + '/account/activate/' + key

        c = {'username': username, 'url': url}
        text_content = render_to_string('customauth/register-email.txt', c)
        html_content = render_to_string('customauth/register-email.html', c)

        subject, from_email, to = 'Confirm Your Email Address', 'Superchamp <noreply@notify.gosuperchamp.com>', email
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def generate_activation_key(self, username):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        secret_key = get_random_string(20, chars)
        return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']
        exclude = ['first_name','last_name','is_active','is_staff','is_superuser','password']

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs={'class': 'form-control'}
        self.fields['email'].widget.attrs={'class': 'form-control'}


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username', 'placeholder': 'Username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Password'}))

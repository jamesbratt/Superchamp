from django import forms

from django.core.exceptions import ValidationError

from routes.models import Route


class UploadTimeForm(forms.Form):
    request = None
    route = forms.ModelChoiceField(Route.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    fitFile = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadTimeForm, self).__init__(*args, **kwargs)
        self.fields['fitFile'].widget.attrs = {'class': 'form-control'}

    def clean_fitFile(self):
        gps_file = self.cleaned_data['fitFile']
        if gps_file.size > 25000000:
            raise ValidationError('The file is too big')

        if gps_file.content_type != 'application/octet-stream':
            raise ValidationError('You can only upload a .FIT file')

        return gps_file

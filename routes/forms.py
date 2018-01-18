from django import forms

from .models import Route


class CreateRouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['title', 'country', 'locality', 'polyline', 'distance', 'start_lat', 'start_long', 'finish_lat', 'finish_long', 'min_elevation', 'max_elevation', 'elevation_gain', 'difficulty']
        exclude = ['user', 'created_date']

    def __init__(self, *args, **kwargs):
        super(CreateRouteForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs = {'class': 'form-control'}
        self.fields['country'].widget.attrs = {'class': 'form-control'}
        self.fields['locality'].widget.attrs = {'class': 'form-control'}
        self.fields['difficulty'].widget.attrs = {'class': 'form-control'}
        self.fields['polyline'].widget = forms.HiddenInput()
        self.fields['distance'].widget = forms.HiddenInput()
        self.fields['start_lat'].widget = forms.HiddenInput()
        self.fields['start_long'].widget = forms.HiddenInput()
        self.fields['finish_lat'].widget = forms.HiddenInput()
        self.fields['finish_long'].widget = forms.HiddenInput()
        self.fields['min_elevation'].widget = forms.HiddenInput()
        self.fields['max_elevation'].widget = forms.HiddenInput()
        self.fields['elevation_gain'].widget = forms.HiddenInput()

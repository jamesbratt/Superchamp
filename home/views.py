from django.shortcuts import render
from django.views.generic import TemplateView
from races.models import Race
from imagekit import ImageSpec, register
from imagekit.processors import ResizeToFill


class FeaturedImage(ImageSpec):
    processors = [ResizeToFill(1920, 500)]
    format = 'JPEG'
    options = {'quality': 60}

register.generator('races:featuredimage', FeaturedImage)


class HomePageView(TemplateView):
    template_name = 'home/home_page.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        fr = Race.objects.filter(is_featured = True).distinct()
        #context['featuredRace'] = fr[0]
        context['metaTitle'] = 'Superchamp | Join in Local Virtual Cycling Events'
        context['metaDescription'] = 'Superchamp lets any cyclist take part in, or organise virtual cycling events right on their own front door.'
        return context

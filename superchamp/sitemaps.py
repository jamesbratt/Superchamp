from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap

class StaticSitemap(Sitemap):
     priority = 0.8
     changefreq = 'weekly'

     # The below method returns all urls defined in urls.py file
     def items(self):
        siteList = ['customauth:login','customauth:register','races:race-list','home:home-page',]
        return siteList

     def location(self, item):
         return reverse(item)

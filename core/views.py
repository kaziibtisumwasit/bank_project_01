from django.shortcuts import render

from django.views.generic import TemplateView

# Create your views here.
##There is no logical things , no need to show details & forms so thats why here we use TemplateView
#just render template
class HomeView(TemplateView):
    template_name = 'index.html'
    
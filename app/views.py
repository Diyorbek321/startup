from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from app.forms import MessageForm



# Create your views here.
class Index(CreateView):
    form_class = MessageForm
    template_name = 'index.html'
    success_url = reverse_lazy('home')
from django.views.generic import ListView, TemplateView
from .models import Board


class Index(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'index.html'


class Contacts(TemplateView):
    template_name = 'contacts.html'

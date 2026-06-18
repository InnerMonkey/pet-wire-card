from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WireVariant, WirePiece

class WireWariantListView(ListView):
    model = WireVariant
    template_name = 'wires/wirevariant_list.html'
    context_object_name = 'variants'
    paginate_by = 50



# Create your views here.

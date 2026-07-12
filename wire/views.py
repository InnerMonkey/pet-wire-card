from django.shortcuts import render
from django.db.models import Prefetch, Count, Q, Sum
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WireVariant, WirePiece, WireType


class WireWariantListView(ListView):
    model = WireVariant
    template_name = "wire/wirevariant_list.html"
    context_object_name = "variants"
    paginate_by = 50


class WireTypeListView(ListView):
    model = WireType
    template_name = "wiretype_list.html"
    context_object_name = "types"
    paginate_by = 50


class WirePieceListView(ListView):
    model = WirePiece
    template_name = "wire/wirepiece_list.html"
    context_object_name = "pieces"
    paginate_by = 50


class WireInventoryView(ListView):
    model = WireType
    template_name = "wire/wireinventory_list.html"
    context_object_name = "wire_types"
    paginate_by = 50

    def get_queryset(self):
        queryset = (
            WireType.objects.annotate(pieces_count=Count("variants__pieces"))
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=WireVariant.objects.annotate(
                        total_length=Sum("pieces__length_m"),
                        pieces_count=Count("pieces"),
                    )
                    .order_by("cores", "mm2")
                    .prefetch_related("pieces"),
                )
            )
            .order_by("name")
        )
        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(variants__cores__icontains=search)
                | Q(variants__mm2__icontains=search)
                | Q(variants__manufacturer__name__icontains=search)
                | Q(variants__color__name__icontains=search)
            ).distinct()
        return queryset


# Create your views here.

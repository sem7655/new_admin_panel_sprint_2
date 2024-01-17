from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
import json
from django.core import serializers

from movies.models import Filmwork, PersonFilmwork, RoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        filmworks = Filmwork.objects.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(
                'person__full_name',
                filter=Q(personfilmwork__role=RoleType.ACTOR),
                distinct=True,
            ),
            directors=ArrayAgg(
                'person__full_name',
                filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                distinct=True,
            ),
            writers=ArrayAgg(
                'person__full_name',
                filter=Q(personfilmwork__role=RoleType.WRITER),
                distinct=True,
            )
        )
        return filmworks

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    paginate_by = 50
    http_method_names = ['get']

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)
        if page.has_previous():
            prev = page.previous_page_number()
        else:
            prev = None
        if page.has_next():
            next = page.next_page_number()
        else:
            next = None

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': prev,
            'next': next,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        context = queryset.first()
        return context
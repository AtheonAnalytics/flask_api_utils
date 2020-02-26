# -*- coding: utf-8 -*-
from flask import request
from sqlalchemy_filters.models import get_model_from_spec, Field, get_default_model, auto_join
from sqlalchemy_filters.sorting import Sort as BaseSort

from flask_api_utils.constants import ORDERING_PARAM, ORDER_PATTERN

SORT_ASCENDING = 'asc'
SORT_DESCENDING = 'desc'


def sort_query(query, view):
    params = request.args.get(ORDERING_PARAM)
    if params:
        fields = [param.strip() for param in params.split(',')]
        ordering = remove_invalid_fields(query, fields, view.ordering_fields)
        if ordering:
            # Rebuild specs
            spec = build_spec(view.ordering_fields, ordering)
            query = apply_sort(query, spec)
    elif get_default_ordering_spec(view):
        spec = get_default_ordering_spec(view)
        query = apply_sort(query, spec)

    return query


def get_default_ordering_spec(view):
    ordering = getattr(view, 'ordering', None)
    return ordering


def remove_invalid_fields(query, fields, ordering_fields):
    if ordering_fields:
        valid_fields = ordering_fields

        valid_fields = [
            (item, item) if isinstance(item, str) else item
            for item in valid_fields
        ]
        valid_fields = [item[0] for item in valid_fields]
    else:
        valid_fields = {}

    return [term for term in fields if term.lstrip('-') in valid_fields and ORDER_PATTERN.match(term)]


def build_spec(ordering_fields, ordering):
    spec = []
    for term in ordering:
        field_spec = ordering_fields[term.lstrip('-')]
        field_spec['direction'] = 'desc' if term.startswith('-') else 'asc'

        spec.append(field_spec)

    return spec


class Sort(BaseSort):
    def format_for_sqlalchemy(self, query, default_model):
        sort_spec = self.sort_spec
        direction = self.direction
        field_name = self.field_name

        model = get_model_from_spec(sort_spec, query, default_model)

        # Check if json field
        field_specs = field_name.split(".")
        if len(field_specs) > 1:
            field_name = field_specs[0]
            inner_field = field_specs[1]

            field = Field(model, field_name)
            sqlalchemy_field = field.get_sqlalchemy_field()

            if direction == SORT_ASCENDING:
                sort_fnc = sqlalchemy_field[inner_field].astext.asc
            elif direction == SORT_DESCENDING:
                sort_fnc = sqlalchemy_field[inner_field].astext.desc
        else:
            field = Field(model, field_name)
            sqlalchemy_field = field.get_sqlalchemy_field()

            if direction == SORT_ASCENDING:
                sort_fnc = sqlalchemy_field.asc
            elif direction == SORT_DESCENDING:
                sort_fnc = sqlalchemy_field.desc

        if self.nullsfirst:
            return sort_fnc().nullsfirst()
        elif self.nullslast:
            return sort_fnc().nullslast()
        else:
            return sort_fnc()


def get_named_models(sorts):
    models = set()
    for sort in sorts:
        models.update(sort.get_named_models())
    return models


def apply_sort(query, sort_spec):
    """Apply sorting to a :class:`sqlalchemy.orm.Query` instance.

    :param sort_spec:
        A list of dictionaries, where each one of them includes
        the necesary information to order the elements of the query.

        Example::

            sort_spec = [
                {'model': 'Foo', 'field': 'name', 'direction': 'asc'},
                {'model': 'Bar', 'field': 'id', 'direction': 'desc'},
                {
                    'model': 'Qux',
                    'field': 'surname',
                    'direction': 'desc',
                    'nullslast': True,
                },
                {
                    'model': 'Baz',
                    'field': 'count',
                    'direction': 'asc',
                    'nullsfirst': True,
                },
            ]

        If the query being modified refers to a single model, the `model` key
        may be omitted from the sort spec.

    :returns:
        The :class:`sqlalchemy.orm.Query` instance after the provided
        sorting has been applied.
    """
    if isinstance(sort_spec, dict):
        sort_spec = [sort_spec]

    sorts = [Sort(item) for item in sort_spec]

    default_model = get_default_model(query)

    sort_models = get_named_models(sorts)
    query = auto_join(query, *sort_models)

    sqlalchemy_sorts = [
        sort.format_for_sqlalchemy(query, default_model) for sort in sorts
    ]

    if sqlalchemy_sorts:
        query = query.order_by(*sqlalchemy_sorts)

    return query

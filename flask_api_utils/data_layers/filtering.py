from flask import request
from sqlalchemy_filters import apply_filters


def filter_query(query, view):
    spec = getattr(view, 'filter_fields', None)
    if spec:
        filter_spec = []
        for key, spec in spec.items():
            value = request.args.get(key)
            if value:
                spec['value'] = value
                filter_spec.append(spec)

        query = apply_filters(query, filter_spec)

    return query

from flask import request
from sqlalchemy_filters import apply_filters


def filter_query(query, view, data=None):
    spec = getattr(view, 'filter_fields', None)
    if spec:
        data_transformers = spec.pop('data_transformers', {})

        filter_spec = []
        data = data if data else request.args
        for key, spec in spec.items():
            value = data.get(key)
            if value:
                if key in data_transformers:
                    value = data_transformers[key]

                spec['value'] = value
                filter_spec.append(spec)

        query = apply_filters(query, filter_spec)

    return query

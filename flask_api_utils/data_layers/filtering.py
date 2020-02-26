from flask import request
from sqlalchemy_filters import apply_filters


def filter_query(query, spec):
    filter_spec = []
    for key, spec in spec.items():
        value = request.args.get(key)
        if value:
            spec['value'] = value
            filter_spec.append(spec)

    query = apply_filters(query, filter_spec)

    return query

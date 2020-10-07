from flask_restx import reqparse


def create_partial_parser(parser):
    partial_parser = parser.copy()
    for arg in partial_parser.args:
        arg.required = False
        arg.store_missing = False

    return partial_parser


pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, location='args')
pagination_arguments.add_argument('per_page', type=int, default=10, location='args')

bulk_delete_parser = reqparse.RequestParser()
bulk_delete_parser.add_argument('ids', type=list, required=True, location='json')

# Paging
from flask_api_utils.parsers import pagination_arguments


def paginate_query(query):
    paging_args = pagination_arguments.parse_args()

    return query.paginate(**paging_args, error_out=False)

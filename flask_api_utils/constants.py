import re

ORDER_PATTERN = re.compile(r'\?|[-+]?[.\w]+$')
ORDERING_PARAM = 'ordering'
SEARCH_PARAM = 'search'

import asyncio
from functools import reduce

from deepmerge import always_merger


async def fetch_all_pages_per_url(client, method_string, **kwargs):
    func = getattr(client, method_string)
    if not callable(func):
        raise TypeError('Need a callable, got %r' % func)

    params = {} if not kwargs else kwargs

    first = await func(**params)
    result = await asyncio.gather(
        *[
            func(**always_merger.merge(params, {"params": {"page": page}}))
            for page in range(2, first["pages"] + 1)
        ]
    )
    result.append(first)
    return result


async def fetch_all_urls(client, method_string, object_lists):
    results = await asyncio.gather(
        *[
            fetch_all_pages_per_url(client, method_string, **{k: i})
            for k, v in object_lists.items()
            for i in v
        ]
    )
    return results


def parse_items(responses):
    return reduce((lambda x, y: x + y.get('items', [])), responses, [])

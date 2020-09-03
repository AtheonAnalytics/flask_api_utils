import flask
from flask_restplus._http import HTTPStatus
from werkzeug.exceptions import HTTPException


def abort(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message=None, **kwargs):
    '''
    Custom abort function to pass code in response due to the conflict with original code argument name

    Raise a `HTTPException` for the given status `code`.
    Attach any keyword arguments to the exception for later processing.

    :param int status_code: The associated HTTP status code
    :param str message: An optional details message
    :param kwargs: Any additional data to pass to the error payload
    :raise HTTPException:
    '''
    try:
        flask.abort(status_code)
    except HTTPException as e:
        if message:
            kwargs['message'] = str(message)
        if kwargs:
            e.data = kwargs
        raise


def has_perm(organisations, host_name, perm, retailer=None):
    if not organisations or not (host_name in organisations and 'roles' in organisations[host_name]):
        return False

    if not retailer:
        retailer = 'global'

    return perm in organisations[host_name]['roles'].get(retailer, [])


def has_staff_perm(organisations, perm):
    for host_name, organisation in organisations.items():
        if 'roles' in organisation:
            if perm in organisation['roles'].get('global', []):
                return True

    return False


def is_staff(data, claim_name='https://api.skutrak.com/organisations'):
    if data.get('sub'):
        sub = data.get('sub')
        if '@clients' in sub:
            return True

        organisations = data.get(claim_name, {})
    else:
        organisations = data

    for host_name, organisation in organisations.items():
        if 'roles' in organisation:
            for role in organisation['roles'].get('global', []):
                if role.startswith('staff'):
                    return True

    return False

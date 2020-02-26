import flask
from flask_restplus._http import HTTPStatus
from sqlalchemy import or_, and_
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

from functools import wraps

from flask import request, g, current_app
from flask_jwt_extended import get_raw_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import Forbidden

from flask_api_utils.utils import abort


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_raw_jwt()
        g.organisations = jwt_data.get(
            current_app.config["AUTH0_ORGANISATIONS_CLAIM_NAME"], {}
        )
        g.email = jwt_data.get(current_app.config["AUTH0_EMAIL_CLAIM_NAME"])
        g.auth0_id = jwt_data.get(current_app.config["JWT_IDENTITY_CLAIM"])
        return fn(*args, **kwargs)

    return wrapper


def allow_internal_service(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.host != current_app.config.get('CURRENT_SERVICE_HOST'):
            abort(403)

        return func(*args, **kwargs)

    return wrapper


def auth_by(*auth_list):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for auth in auth_list:
                try:
                    af_func = auth(func)
                    return af_func(*args, **kwargs)
                except (Forbidden, NoAuthorizationError) as e:
                    # TODO: Find another solution for generic error handling
                    continue

            abort(403)

        return wrapper

    return actual_decorator


def whitelist_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        source_ip = request.headers.get(current_app.config.get("SOURCE_IP_HEADER"))
        if source_ip not in current_app.config.get("WHITELISTED_IP", []) and not (
                current_app.config.get("DEBUG") and source_ip[:3] in ["172", "192"]
        ):
            abort(403)
        return func(*args, **kwargs)

    return wrapper

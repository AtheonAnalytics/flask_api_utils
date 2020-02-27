from functools import wraps

from flask import g, current_app
from flask_jwt_extended import get_raw_jwt, verify_jwt_in_request


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

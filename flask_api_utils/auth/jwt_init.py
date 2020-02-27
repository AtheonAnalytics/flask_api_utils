import json
from urllib.request import urlopen

from flask import current_app
from jwt.algorithms import RSAAlgorithm

from flask_api_utils.utils import abort
from .core import AuthError


def jwks_decode_key_callback(claims, headers):
    jsonurl = urlopen(current_app.config['JWKS_ENDPOINT'])
    jwks = json.loads(jsonurl.read())
    if headers["alg"] == "HS256":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Invalid header. "
                               "Use an RS256 signed JWT Access Token",
            },
            401,
        )

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == headers["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    return RSAAlgorithm.from_jwk(json.dumps(rsa_key))


def expired_token_callback(expired_token):
    abort(401, code="token_expired", message="Token is expired")


def invalid_token_callback(error_string):
    abort(422, code="invalid_token", message=error_string)


def unauthorized_callback(error_string):
    abort(401, code="unauthorized", message=error_string)


def needs_fresh_token_callback():
    abort(401, code="needs_fresh_token", message="Fresh token required")


def revoked_token_callback():
    abort(401, code="revoked_token", message="Token has been revoked")


def user_loader_error_callback(identity):
    abort(401, code="failed_user_loaded", message="Error loading user")


def verify_claims_failed_callback():
    abort(401, code="failed_claims_verification", message="User claims verification failed")


def config_jwt_manager(jwt):
    jwt.decode_key_loader(jwks_decode_key_callback)
    jwt.expired_token_loader(expired_token_callback)
    jwt.invalid_token_loader(invalid_token_callback)
    jwt.unauthorized_loader(unauthorized_callback)
    jwt.needs_fresh_token_loader(needs_fresh_token_callback)
    jwt.revoked_token_loader(revoked_token_callback)
    jwt.user_loader_error_loader(user_loader_error_callback)
    jwt.claims_verification_failed_loader(verify_claims_failed_callback)

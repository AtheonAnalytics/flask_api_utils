from flask_restx import Api as BaseApi


class Api(BaseApi):
    def make_response(self, data, *args, **kwargs):
        resp = super().make_response(data, *args, **kwargs)

        # Remove content-type header if 204
        if resp.status_code == 204:
            resp.headers.remove('Content-Type')

        return resp

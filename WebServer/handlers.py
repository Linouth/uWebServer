from .response import Response


class RequestHandler():
    """"""

    STATUS = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
    }

    def __init__(self):
        self.methods = {
                'GET': self.on_get,
                'POST': self.on_post,
                'HEAD': self.on_head,
                'PUT': self.on_put,
                'DELETE': self.on_delete,
                'OPTIONS': self.on_options,
                'CONNECT': self.on_connect
        }
        self.response = Response(self.__class__.__name__)

    def get_response(self, req, root):
        self.req = req
        self.root = root
        try:
            self.methods[req.method]()
        except KeyError:
            self.on_Invalid()

        return self.response

    def on_get(self):
        raise NotImplementedError()

    def on_post(self):
        raise NotImplementedError()

    def on_head(self):
        raise NotImplementedError()

    def on_put(self):
        raise NotImplementedError()

    def on_delete(self):
        raise NotImplementedError()

    def on_options(self):
        raise NotImplementedError()

    def on_connect(self):
        raise NotImplementedError()

    def on_invalid(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<class RequestHandler({} {} {})>'.format(self.req.method,
                                                         self.req.path,
                                                         self.req.version)


class DefaultHandler(RequestHandler):
    def on_get(self):
        self.response.init_header(200)
        self.response.content = '<html><body><h1>Welcome!</h1></body></html>'

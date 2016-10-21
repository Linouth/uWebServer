from .__version__ import __version__
import os


class HeaderNotInitializedError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Response():
    """"""

    class Header():
        STATUS = {
                200: 'OK',
                301: 'Moved Permanently',
                400: 'Bad Request',
                404: 'Not Found',
                500: 'Internal Server Error'
        }

        status_line = ''
        response_fields = []

        def __init__(self):
            self.initialized = False

        def init(self, code: int):
            self.status_line = ('HTTP/1.0 {} {}'.format(code,
                                                        self.STATUS[code]))
            self.add('Server', 'uWebServer/{} MicroPython/{}'
                               .format(__version__, os.uname()[2]))
            self.initialized = True

        def add(self, key, value):
            self.response_fields.append('{}: {}'.format(key, value))

        def __str__(self):
            return (self.status_line + '\r\n' +
                    '\r\n'.join(self.response_fields))

    def __init__(self, handler_name):
        self.handler_name = handler_name
        self.header = self.Header()
        self.content = ''
        self.valid = False

    def init_header(self, code: int):
        self.status_code = code
        self.header.init(code)
        self.valid = True

    def get(self):
        if not self.header.initialized:
            raise HeaderNotInitializedError(
                    'Header not Initialized in handler: ' + self.handler_name
            )
        return self.__str__().encode('utf-8')

    def __str__(self):
        return '{}\r\n\r\n{}'.format(self.header, self.content)

    def __repr__(self):
        return '<class Response({}, {})>'\
               .format(self.status_code, self.header.STATUS[self.status_code])

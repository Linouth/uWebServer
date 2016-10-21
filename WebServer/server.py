import socket
import os
from .logging import Logger
from .handlers import RequestHandler, DefaultHandler
from .__version__ import __version__


class Request():
    """
    Request received from the client

    data -- Received data in bytes
    """
    def __init__(self, data):
        lines = [d.strip() for d in data.decode('utf-8').split('\r\n')]

        try:
            self.method, self.path, self.version = lines[0].split(' ')
            self.headers = {k: v for k, v in
                            (l.split(': ')for l in lines[1:-2])}
        except ValueError:
            self.method = None
            self.headers = None

    def __getattr__(self, name):
        try:
            return self.headers[name]
        except IndexError:
            raise AttributeError(name)
        except TypeError as e:
            print('Request TypeError: ' + str(e))
            pass


class Response_old():
    """
    Class to handle requests and create responses

    Should be inherited to configure the on_request events
    if no post_handler given.

    req -- Request instance
    homedir -- The server root directory
    post_handler -- Class or function to handle Post requests
    """

    STATUS = {
            200: 'OK',
            400: 'Bad Request',
            404: 'File not found',
            500: 'Internal server error'
    }
    DIR_LIST = 1

    dir_list = '''
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Index of {cwd}</title>
    </head>
    <body>
        <h1>Index of {cwd}</h1>
        <table style='text-align: center'>
            <tr>
                <th>
                    Filename
                </th>
                <th>
                    Filesize
                </th>
            </tr>
            {}
        </table>
    </body>
</html>
'''
    tabledata = '''<tr>
                <td><a href='{path}'>{filename}</a></td>
                <td>{filesize}K</td>
            </tr>'''

    res_400 = '<center><h1>Bad Request.</h1><hr /></center>'
    res_404 = '<center><h1>File not found.</h1><hr /></center>'
    res_500 = '<center><h1>Internal Server Error.</h1><hr /></center>'

    def __init__(self, req, homedir, post_handler=None):
        self.req = req
        self.homedir = homedir
        self.post_handler = post_handler

        if self.req.method == 'GET':
            self._on_get_request()
        elif self.req.method == 'POST':
            self._on_post_request()
        elif self.req.method == 'HEAD':
            self._on_head_request()
        else:
            self._on_bad_request()

        self.response = bytes('{}\r\n\r\n{}'.format(self.headers,
                                                    self.content), 'utf-8')

    def _on_get_request(self):
        self.content, self.status_code = self.get_content()
        self.headers = self.get_headers(self.status_code)

    def _on_post_request(self):
        if self.post_handler:
            self.post_handler(self)
        else:
            print('Post event not configured')
            self._on_error_request()

    def _on_head_request(self):
        self.content = ''
        _, self.status_code = self.get_content()
        self.headers = self.get_headers(self.status_code)

    def _on_bad_request(self):
        self.content = self.res_400
        self.status_code = 400
        self.headers = self.get_headers(self.status_code)

    def _on_error_request(self):
        self.content = self.res_500
        self.status_code = 500
        self.headers = self.get_headers(self.status_code)

    def get_headers(self, code):
        return '\r\n'.join([
                    'HTTP/1.0 {} {}'.format(code, self.STATUS[code]),
                    'Server: uWebServer/{} MicroPython/{}'.format(__version__,
                                                                  os.uname()[3]
                                                                  ),
                    'Content-Type: text/html'
        ])

    def get_content(self):
        # path = self.homedir + self.req.path
        req_path = self.req.path[:-1] + self.req.path[-1].replace('/', '')
        path = self.homedir + req_path
        try:
            with open(path, 'r') as f:
                return f.read(), 200
        except OSError:
            try:
                dirs = os.listdir(path)
                if 'index.html' in dirs:
                    with open(path + '/index.html', 'r') as f:
                        return f.read(), 200

                if self.DIR_LIST == 1:
                    data = []
                    for d in dirs:
                        p = '{}/{}'.format(path, d)
                        web_path = '{}/{}'.format(req_path, d)
                        data.append({'path': web_path,
                                     'filesize': round(os.stat(p)[6]/1024, 2),
                                     'filename': d})
                    table_html = '\r\n'.join([self.tabledata.format(**d)
                                              for d in data])
                    return self.dir_list.format(table_html, cwd=path), 200
            except OSError:
                return self.res_404, 404

    def __repr__(self):
        return '<class Response({}, {}, {})>'\
                .format(self.status_code, self.STATUS[self.status_code],
                        self.homedir)


class WebServer():
    """
    HTTP Web server for ESP8266 with MicroPython

    port -- The port to host the Webserver on
    host -- Host to host the Webserver on
    root -- The root directory of the Webserver
    handler -- Class to handle all requests and act as a Response
    post_handler -- Class or function to handle Post requests
                    (send through to handler)
    """

    def __init__(self, port=80, host='0.0.0.0',
                 root=os.getcwd()):
        self.handlers = [DefaultHandler()]
        self.port = port
        self.host = host

        # Remove trailing slash
        root = root[:-1] + root[-1].replace('/', '')
        self.root = root

        self.logger = Logger()

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))

    def add_handler(self, handler: RequestHandler):
        self.handlers.append(handler)

    def start(self):
        self.logger.log('Starting WebServer')
        self.socket.listen(5)

        while True:
            client, client_info = self.socket.accept()
            data = client.recv(1024)
            req = Request(data)

            for handler in reversed(self.handlers):
                res = handler.get_response(req, self.root)
                if res:
                    break

            self.logger.log({
                'host': client_info[0],
                'method': req.method,
                'path': req.path,
                'version': req.version,
                'code': res.status_code,
                'code_info': res.header.STATUS[res.status_code]
            }, self.logger.CONNECTION)

            client.send(res.get())

            client.close()
        self.stop()

    def stop(self):
        self.logger.log('Stopping WebServer')
        self.socket.close()

    def __repr__(self):
        return '<class WebServer({}, {}, {})>'\
                .format(self.host, self.port, self.root)


def main():
    server = WebServer(80, root='/srv')
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == '__main__':
    main()

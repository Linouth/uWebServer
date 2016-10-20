import socket
import os
from .logging import Logger
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
            self.headers = {k: v for k, v in (l.split(': ') for l in lines[1:-2])}
        except ValueError:
            self.method=None
            self.headers=None

    def __getattr__(self, name):
        try:
            return self.headers[name]
        except IndexError:
            raise AttributeError(name)
        except TypeError:
            pass


class Response():
    """"""

    STATUS = {
            200: 'OK',
            400: 'Bad Request',
            404: 'File not found',
            500: 'Internal server error'
    }
    EXPLORER = 1

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

    def __init__(self, req, homedir):
        self.req = req
        self.homedir = homedir

        if self.req.method == 'GET':
            self._on_get_request(self.req)
        elif self.req.method == 'POST':
            self._on_post_request(self.req)
        else:
            self._on_bad_request()

        self.response = bytes('{}\r\n\r\n{}'.format(self.headers,
                                                    self.content), 'utf-8')

    def _on_get_request(self, req):
        self.content, self.status_code = self._get_content()
        self.headers = self._get_headers(self.status_code)

    def _on_post_request(self, req):
        pass

    def _on_bad_request(self):
        self.content = self.res_400
        self.status_code = 400
        self.headers = self._get_headers(self.status_code)

    def _on_error_request(self):
        self.content = self.res_500
        self.status_code = 500
        self.headers = self._get_headers(self.status_code)

    def _get_headers(self, code):
        return '\r\n'.join([
                    'HTTP/1.0 {} {}'.format(code, self.STATUS[code]),
                    'Server: uWebServer/{} MicroPython/{}'.format(__version__,
                                                                  os.uname()[3]
                                                                  ),
                    'Content-Type: text/html'
        ])

    def _get_content(self):
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

                if self.EXPLORER == 1:
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
    homedir -- The root directory of the Webserver
    """

    def __init__(self, port=80, host='0.0.0.0', homedir=os.getcwd()):
        self.port = port
        self.host = host
        self.homedir = homedir

        self.logger = Logger()

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))

    def start(self):
        self.logger.log('Starting WebServer')
        self.socket.listen(5)

        while True:
            client, client_info = self.socket.accept()
            data = client.recv(1024)
            req = Request(data)
            res = Response(req, self.homedir)

            self.logger.log({
                'host': client_info[0],
                'method': req.method,
                'path': req.path,
                'version': req.version,
                'code': res.status_code,
                'code_info': res.STATUS[res.status_code]
            }, self.logger.CONNECTION)

            client.send(res.response)

            client.close()

    def stop(self):
        self.logger.log('Stopping WebServer')
        self.socket.close()

    def __repr__(self):
        return '<class WebServer({}, {}, {})>'\
                .format(self.host, self.port, self.homedir)


def main():
    server = WebServer(80, homedir='/srv')
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == '__main__':
    main()

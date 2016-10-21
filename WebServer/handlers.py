from .response import Response
import os


class RequestHandler():
    """"""

    res_404 = '<html><body><center><h1>File not found.</h1>' +\
              '<hr /></center></html></body>'

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
        self.response.valid = False

        self.req = req
        self.root = root
        try:
            self.methods[req.method]()
        except KeyError:
            self.on_Invalid()

        return self.response if self.response.valid else None

    def get_file(self, req_path):
        # Remove trailing slash
        req_path = req_path[:-1] + req_path[-1].replace('/', '')
        path = self.root + req_path

        try:
            # Check for file
            with open(path, 'r') as f:
                return f.read(), 200
        except OSError:
            # File not found
            try:
                # Check for dir
                dirs = os.listdir(path)
                if 'index.html' in dirs:
                    with open(path + '/index.html', 'r') as f:
                        return f.read(), 200
            except OSError:
                # No file or dir found
                return self.res_404, 404

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
        self.response.content, code = self.get_file(self.req.path)
        self.response.init_header(code)


class DirlistHandler(RequestHandler):
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
    table_data = '''
            <tr>
                <td><a href='{path}'>{filename}</a></td>
                <td>{filesize}K</td>
            </tr>'''

    def on_get(self):
        try:
            self.response.content, code = self.get_dirs(self.req.path)
            self.response.init_header(code)
        except TypeError:
            self.response.valid = False

    def get_dirs(self, req_path):
        """Get HTML formated dirlist"""
        # Remove trailing slash
        req_path = req_path[:-1] + req_path[-1].replace('/', '')
        path = self.root + req_path

        try:
            dirs = os.listdir(path)
            data = []
            for d in dirs:
                p = '{}/{}'.format(path, d)
                url = '{}/{}'.format(req_path, d)
                data.append({'path': url,
                             'filesize': round(os.stat(p)[6]/1024, 2),
                             'filename': d})
            table_html = '\r\n'.join([self.table_data.format(**d)
                                      for d in data])
            return self.dir_list.format(table_html, cwd=req_path), 200
        except OSError:
            return None

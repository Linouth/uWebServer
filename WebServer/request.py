class Request():
    """Request received from the client

    data -- Received data in bytes
    host -- Address from client
    """
    def __init__(self, data):
        lines = [d.strip() for d in data.decode('utf-8').split('\r\n')]
        self.boundary = None

        try:
            self.method, self.path, self.version = lines[0].split(' ')
            self.headers = {k: v for k, v in
                            (l.split(': ') for l in lines[1:-2])}
            self.host = self.headers['Host']

            # TODO: Save post data in Request.post.fieldname format
            #       (Also for big files)
            if 'multipart/form-data' in self.content_type:
                self.boundary = self.content_type\
                                .split(' ')[-1].split('=')[1]

            if 'application/x-www-form-urlencoded' in self.content_type:
                # Split data to dict format name:value
                self.post_data = {k: v for k, v in (f.split('=')
                                  for f in lines[-1].split('&'))}
        except ValueError:
            self.method = None
            self.headers = None
            self.host = None

    def add_data(self, data):
        self.raw_data = data
        boundary = '--' + self.boundary

        forms = data.split((boundary + '\r\n').encode('utf-8'))[1:]
        forms[-1] = forms[-1].replace(('\r\n' + boundary + '--\r\n')
                                      .encode('utf-8'), b'')
        for i in range(len(forms[:-1])):
            forms[i] = forms[i].rstrip(b'\r\n')

        self.forms = []
        for form in forms:
            f = {}
            l = form.split(b'\r\n', 3)
            for i in range(2):
                p = l[i].decode('utf-8').split(': ')
                f[p[0]] = p[1]
            f['data'] = l[3]
            self.forms.append(f)

    def __getattr__(self, name):
        try:
            return self.headers['-'.join([n.capitalize()
                                          for n in name.split('_')])]
        except IndexError:
            raise AttributeError(name)
        except TypeError as e:
            print('Request TypeError: ' + str(e))
            pass

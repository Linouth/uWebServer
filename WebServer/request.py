class Request():
    """Request received from the client

    data -- Received data in bytes
    host -- Address from client
    """
    def __init__(self, data):
        lines = [d.strip() for d in data.decode('utf-8').split('\r\n')]
        self.boundary = 'NoBoundAry'

        try:
            self.method, self.raw_path, self.version = lines[0].split(' ')
            self.headers = {k: v for k, v in
                            (l.split(': ') for l in lines[1:-2])}
            self.host = self.headers['Host']

            self.path = self.raw_path.split('?', 1)[0]

            # Save GET data to get dict
            if '?' in self.raw_path:
                data = self.raw_path.split('?', 1)[1]
                self.get = {k: v for k, v in
                            (l.split('=', 1) for l in data.split('&'))}

            if self.method == 'POST':
                if 'boundary=' in self.headers['Content-Type']:
                    self.boundary = self.headers['Content-Type']\
                                    .split(' ')[-1].split('=')[1]

                # POST data available
                if lines[-1] is not '':
                    if self.boundary in lines[-1]:
                        # Handle 'multipart/form-data'
                        print('Handle multipart/form-data')
                        pass
                    else:
                        self.post = {k: v for k, v in
                                     (l.split('=', 1) for l in
                                         lines[-1].split('&'))}
                    print(self.post)

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

    # def __getattr__(self, name):
    #     try:
    #         return self.headers['-'.join([n.capitalize()
    #                                       for n in name.split('_')])]
    #     except IndexError:
    #         # raise AttributeError(name)
    #         return None
    #     except TypeError as e:
    #         print('Request TypeError: ' + str(e))
    #         pass

class Request():
    """
    Request received from the client

    data -- Received data in bytes
    host -- Address from client
    """
    def __init__(self, host, data):
        self.host = host

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

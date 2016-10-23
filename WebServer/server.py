from .handlers import RequestHandler, DefaultHandler
from .logging import Logger
from .request import Request
import os
import socket
import time


class WebServer():
    """
    HTTP Web server for ESP8266 with MicroPython

    port -- The port to host the Webserver on
    host -- Host to host the Webserver on
    root -- The root directory of the Webserver (default $(cwd))
    """

    def __init__(self, port=80, host='0.0.0.0',
                 root=os.getcwd()):
        self.handlers = [DefaultHandler()]
        self.port = port
        self.host = host

        # Remove trailing slash
        root = root.rstrip('/')
        self.root = root

        self.logger = Logger()

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))

    def add_handler(self, handler: RequestHandler):
        """Add RequestHandler to the WebServer.
        Handlers are prioritized based on the order,
        meaning last added handler is used first.

        handler -- RequestHandler to add
        """

        self.handlers.append(handler)

    def start(self):
        """Start the WebServer"""
        self.logger.log('Starting WebServer')
        self.socket.listen(5)

        while True:
            client, client_info = self.socket.accept()
            head = client.recv(1024)

            req = Request(head)
            # if req.boundary:
            #     data = self._recv_data(client)
            #     req.add_data(data)

            for handler in reversed(self.handlers):
                res = handler.get_response(req, self.root, self.logger)
                if res:
                    break

            self.logger.log({
                'host': client_info[0],
                'method': req.method,
                'path': req.raw_path,
                'version': req.version,
                'code': res.status_code,
                'code_info': res.header.STATUS[res.status_code],
                'handler': res.handler_name
            }, self.logger.CONNECTION)

            client.send(res.get())

            client.close()
        self.stop()

    def stop(self):
        self.logger.log('Stopping WebServer')
        self.socket.close()

    def _recv_data(self, socket, buff=2048, timeout=1.5):
        socket.setblocking(False)

        data = []

        t = time.time()
        while True:
            if time.time()-t > timeout:
                break

            try:
                d = socket.recv(buff)
                if d:
                    data.append(d)
                else:
                    time.sleep(0.1)
            except:
                pass
        return b''.join(data)

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

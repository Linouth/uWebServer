import WebServer
from WebServer.handlers import DirlistHandler


# WebServer.server.main()
server = WebServer.WebServer(4444)
server.add_handler(DirlistHandler())
try:
    server.start()
except KeyboardInterrupt:
    pass
finally:
    server.stop()

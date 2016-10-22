import WebServer
from WebServer.handlers import DirlistHandler, IndexHandler, UploadHandler


# WebServer.server.main()
server = WebServer.WebServer(4444)
server.add_handler(DirlistHandler())
server.add_handler(IndexHandler())
server.add_handler(UploadHandler())
try:
    server.start()
except KeyboardInterrupt:
    pass
finally:
    server.stop()

import WebServer


# WebServer.server.main()
server = WebServer.WebServer(4444)
try:
    server.start()
except KeyboardInterrupt:
    pass
finally:
    server.stop()

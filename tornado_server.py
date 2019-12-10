"""
    __file__ = tornado_server.py
    __description = Handle different tornado server events.
    __author__ = Souvik De, Devansh Mittal
    __References__ = https://os.mbed.com/cookbook/Websockets-Server
"""

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import DAL
import server as Server

import base64

class WSHandler(tornado.websocket.WebSocketHandler):
    """Parent class for web socket"""

    def open(self):
        """Executed when client connects"""
        print('New Connection')

    def on_message(self, message):
        """Executes when server receives message
           message - message received by server from client
        """
        print('message received:  %s' % message)

    def on_close(self):
        """Executes when connection closed"""
        print('Connection Closed')

    def check_origin(self, origin):
        return True

application = tornado.web.Application([
    (r'/ws', WSHandler),
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Tornado Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()
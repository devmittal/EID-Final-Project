#!/usr/bin/env python3

import boto3
import DAL
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import asyncio
import base64

global sqs
global s3

# Get the service resource
sqs = boto3.resource('sqs')
s3 = boto3.client('s3')

# Get the queue
def GetSQSQueueObject():
    return sqs.get_queue_by_name(QueueName='Magic-Wand.fifo')
            
class WSHandler(tornado.websocket.WebSocketHandler):
    """Parent class for web socket"""
    def open(self):
        """Executed when client connects"""
        print('new connection')
        
    def on_message(self, message):
        """Executes when server receives message
           message - message received by server from client
        """
        print('Message Received: ' + message)

        if message == 'Start Polling':
            GetSQSQueueData()

    def on_close(self):
        """Executes when connection closed"""
        print('connection closed')
        
    def check_origin(self, origin):
        return True

    def GetSQSQueueData(self):
        count = 0
        label = ""
        confirmation = ""
        image_bucket = 'eid-superproject-image'
        object_name = 'images/object.jpg'
        downloaded_image = 'downloaded_images/image.jpg'

        queue = GetSQSQueueObject()

        while (1):
            # Process messages by printing out body and optional author name
            for message in self.queue.receive_messages():
                # Print out the body
                print('Message -> {0}'.format(self.message.body))

                if count == 0:
                    if message.body == "identify.":
                        DAL.InsertToCommand(self.message.body, 'Yes')
                        self.count += 1
                    else:
                        DAL.InsertToCommand(self.message.body, 'No')
                        self.count = 0
                elif message.body == "image":
                    print('Dowloading image from s3')
                    s3.download_file(image_bucket, object_name, downloaded_image)
                    with open("downloaded_images/image.jpg", "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    self.write_message(encoded_string)
                    self.count += 1
                elif count == 2:
                    self.label = self.message.body
                    self.write_message(self.label)
                    self.count += 1
                else:
                    self.confirmation = self.message.body
                    if self.confirmation == "correct":
                        DAL.InsertToObject(self.label, "correct")
                        DAL.InsertToCommand(self.confirmation, "Yes")
                        self.write_message(self.confirmation)
                    elif self.confirmation == "wrong":
                        DAL.InsertToObject(self.label, "wrong")
                        DAL.InsertToCommand(self.confirmation, "Yes")
                        self.write_message(self.confirmation)
                    else:
                        DAL.InsertToObject(self.label, "unclear")
                        DAL.InsertToCommand(self.confirmation, "No")
                        self.write_message("Inconclusive")
                    self.count += 1
                    self.message.delete()
                    break;
                # Let the queue know that the message is processed
                self.message.delete()

                self.count = self.count % 4
    
    
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
            
def CreateTornadoServer():
    http_server = tornado.httpserver.HTTPServer(application)
    asyncio.set_event_loop(asyncio.new_event_loop())
    http_server.listen(6868)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    CreateTornadoServer()
    #GetSQSQueueData()

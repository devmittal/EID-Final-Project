#!/usr/bin/env python3

"""
	__file__ = server.py
	__description = Sends data to Web Client via Tornado Server, Polls on SQS Queue & Communicates with DA:
	__author__ = Souvik De, Devansh Mittal
"""

import boto3
import DAL
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import asyncio

import base64

# Get the service resource
sqs = boto3.resource('sqs')
s3 = boto3.client('s3')

def GetSQSQueueObject():
    return sqs.get_queue_by_name(QueueName='Magic-Wand.fifo')

def GetSQSQueueData():
    """Poll on SQS Queue to retrieve dataprocessed Data from AWS"""
    queue = GetSQSQueueObject()
    
    count = 0
    label = ""
    image_bucket = 'eid-superproject-image'
    object_name = 'images/object.jpg'
    downloaded_image = 'downloaded_images/image.jpg'

    while(1):
        # Process messages by printing out body and optional author name
        for message in queue.receive_messages():
            # Print out the body
            print('Message -> {0}'.format(message.body))

            """Sequeced in the order - Command, Retrieve Image, Detect Label & Spoken Acknowledgement"""""
            if count == 0:
                expected_string = "identify. identifying. identified."
                if message.body in expected_string:
                    DAL.InsertToCommand(message.body, 'Yes')
                    count += 1
                else:
                    DAL.InsertToCommand(message.body, 'No')
                    count = 0
            elif message.body == "image":
                print('Dowloading image from s3')
                s3.download_file(image_bucket, object_name, downloaded_image)
                count += 1
            elif count == 2:
                label = message.body
                count += 1
            else:
                confirmation = message.body
                if confirmation == "correct.":
                    DAL.InsertToObject(label, "correct")
                    DAL.InsertToCommand(confirmation, "Yes")
                elif confirmation == "wrong.":
                    DAL.InsertToObject(label, "wrong")
                    DAL.InsertToCommand(confirmation, "Yes")
                else:
                    DAL.InsertToObject(label, "unclear")
                    DAL.InsertToCommand(confirmation, "No")
                message.delete()
                count += 1
                return label, confirmation
            # Let the queue know that the message is processed
            message.delete()

            count = count % 4
            
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
            label, confirmation = GetSQSQueueData()
            with open("downloaded_images/image.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            self.write_message(encoded_string)
            self.write_message(label)
            if(confirmation == 'correct.' or confirmation == 'wrong.'):
                self.write_message(confirmation)
            else:
                self.write_message("Inconclusive")

        if message == 'Voice Statistics':
            result = DAL.GetCommandData()
            self.write_message(str(result[0][1]) + " " + str(result[1][1]))

        if message == 'Detection Statistics':
            result = DAL.GetObjectData()
            self.write_message(str(result[0][1]) + " " + str(result[1][1]) + " " + str(result[2][1]))

        if message == 'Detection Data':
            objects = ""
            objects = DAL.GetObjectTable()
            self.write_message(objects)
            
        if message == 'Command Data':
            commands = ""
            commands = DAL.GetCommandTable()
            self.write_message(commands)

    def on_close(self):
        """Executes when connection closed"""
        print('connection closed')
        
    def check_origin(self, origin):
        return True    
    
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

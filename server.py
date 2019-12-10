#!/usr/bin/env python3

import boto3
import DAL

count = 0
label = ""
confirmation = ""
image_bucket='eid-superproject-image'
object_name='images/object.jpg'
downloaded_image='downloaded_images/image.jpg'

# Get the service resource
sqs = boto3.resource('sqs')
s3 = boto3.client('s3')

# Get the queue
queue = sqs.get_queue_by_name(QueueName='Magic-Wand.fifo')

while(1):
    # Process messages by printing out body and optional author name
    for message in queue.receive_messages():
        # Print out the body and author (if set)
        print('Message -> {0}'.format(message.body))

        if count == 0:
            if message.body == "identify.":
                DAL.InsertToCommand(message.body, 'Yes')
            else:
                DAL.InsertToCommand(message.body, 'No')
        elif message.body == "image":
            print('Dowloading image from s3')
            s3.download_file(image_bucket, object_name, downloaded_image)
        elif count == 2:
            label = message.body
        else:
            confirmation = message.body
            if confirmation == "correct":
                DAL.InsertToObject(label, "correct")
                DAL.InsertToCommand(confirmation, "Yes")
            elif confirmation == "wrong":
                DAL.InsertToObject(label, "wrong")
                DAL.InsertToCommand(confirmation, "Yes")
            else:
                DAL.InsertToObject(label, "inconclusive")
                DAL.InsertToCommand(confirmation, "No")
        # Let the queue know that the message is processed
        message.delete()

        count = (count + 1) % 4

#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
import logging
import boto3
import json
import os

camera = PiCamera()
camera.rotation = 180
camera.resolution = (1296,972)

image_path = "images/object.jpg"
image_bucket = 'eid-superproject-image'

if os.path.exists(image_path):
	os.remove(image_path)

camera.start_preview()

sleep(5)

camera.capture(image_path)

camera.stop_preview()

client = boto3.client('rekognition')
s3_client = boto3.client('s3')

with open(image_path, 'rb') as image:
	image_stream = image.read()
	
try:
	resp = s3_client.upload_file(image_path, image_bucket, image_path)
except ClientError as e:
	logging.error(e)
	
response = client.detect_labels(Image={'Bytes':image_stream},
								MaxLabels=1)

json_string = json.dumps(response)

label_object = json.loads(json_string)

index_object = label_object["Labels"][0]

print(json.dumps(index_object["Name"]))
								
#print(json.dumps(label_object["Labels"][0]["Name"]))

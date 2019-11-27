#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
import pyaudio
import wave
import logging
import boto3
import time
from botocore.exceptions import ClientError
import json
import requests
import os
import pygame


global image_path
global rekognition_client

image_path = "images/object.jpg"
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 5 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test1.wav' # name of .wav file
bucket_name = 'eid-superproject'

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
       Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# purpose: get and return the transcript structure given the provided uri
def getTranscript( transcriptURI ):
    #Reference: https://sunjackson.github.io/2018/08/10/73b0c6a36db932d181f93b01831e3425/
   
    # Get the resulting Transcription Job and store the JSON response in transcript
    result = requests.get( transcriptURI )

    return result.text

def IsAudioTranscriptionSuccess(file_name, bucket):
    """Transcribe file uploaded to AWS s3 and check if it is equal to "identify"
       Reference: https://docs.aws.amazon.com/code-samples/latest/catalog/python-transcribe-GettingStarted.py.html
       Input: file_name - File to be transcribed
       	      bucket - bucket from where the file is to be transcribed
       Return: 1 - Image is to be captured
               0 - Image is not to be captured
    """

    transcribe = boto3.client('transcribe')
    s3 = boto3.client('s3')

    job_name = "Test_EID12345"
    result_file_name = "%s.json" % (file_name)

    #Constructing audio file url at s3
    job_uri = "s3://%s/%s" % (bucket, file_name)

    transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US'
    #OutputBucketName=bucket
    )
	
    #Keep looping until transcript ready
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print("Ready")
    # Now get the transcript JSON from AWS Transcribe
    transcript = getTranscript( str(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) ) 
    
    #Convert to dict
    data = json.loads(transcript)
    Actual_Transcript = data['results']['transcripts'][0]['transcript']
    print("Spoken CMD = " + Actual_Transcript)
    expected_string = "identify. identified. identifying."
    if(Actual_Transcript in expected_string):
        return 1
    else:
        return 0

def capture_audio():
    """Capture audio from mic
       Reference: https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone
    """

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1, rate = samp_rate, channels = chans, input_device_index = dev_index,input = True, frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)

    print("finished recording") 

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def Configure_Camera():
    global camera
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (1296,972)
    
def Capture_Image():
    if os.path.exists(image_path):
        os.remove(image_path)
    
    camera.start_preview()
    
    sleep(5)
    
    camera.capture(image_path)
    
    camera.stop_preview()
    
def Recognize_Image():
    with open(image_path, 'rb') as image:
        image_stream = image.read()
    
    response = client.detect_labels(Image={'Bytes':image_stream},
								MaxLabels=1)

    json_string = json.dumps(response)

    label_object = json.loads(json_string)

    index_object = label_object["Labels"][0]

    return json.dumps(index_object["Name"])
    
def play(filename):
    """Output audio on speaker
       Reference: https://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python
       input: filename - name of audio file to be played""" 
    
    print("Playing output")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
         pygame.time.Clock().tick(10)

def speak(text, format='ogg_vorbis', voice='Brian'):
    """Send text to AWS polly and receive converted audio
       Reference: https://medium.com/@julsimon/johnny-pi-i-am-your-father-part-4-adding-cloud-based-vision-8830c2676113
       input: text: text to be converted to audio
              format: format of output audio file
              voice: AWS voice to output audio file"""
    
    polly = boto3.client('polly')
    
    filename="/home/pi/Desktop/Magic_Wand/EID-Final-Project/Output_Audio/label.ogg"
    
    resp = polly.synthesize_speech(OutputFormat=format, Text=text, VoiceId=voice)
    
    soundfile = open(filename, 'wb')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()
    play(filename)
    os.remove(filename)
    
if __name__ == '__main__':
	client = boto3.client('rekognition')
	
	Configure_Camera()
	capture_audio()
	upload_file(wav_output_filename, bucket_name)
	if IsAudioTranscriptionSuccess(wav_output_filename, bucket_name):
		Capture_Image()
		image_label = Recognize_Image() + "is the object identifieddd"
		print(image_label)
		speak(image_label)
    

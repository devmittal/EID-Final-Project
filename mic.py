#!/usr/bin/env python3

import pyaudio
import wave
import logging
import boto3
import time
from botocore.exceptions import ClientError
import json
import requests

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 5 # seconds to record
dev_index = 1 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test1.wav' # name of .wav file
bucket_name = 'eid-superproject'

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

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
    # Get the resulting Transcription Job and store the JSON response in transcript
    result = requests.get( transcriptURI )

    return result.text

def transcribe_file(file_name, bucket):
    
    transcribe = boto3.client('transcribe')
    s3 = boto3.client('s3')

    job_name = "Test_EID11"
    result_file_name = "%s.json" % (file_name)
    job_uri = "s3://%s/%s" % (bucket, file_name)

    transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US'
    #OutputBucketName=bucket
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print("Ready")
    # Now get the transcript JSON from AWS Transcribe
    transcript = getTranscript( str(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) ) 
    
    data = json.loads(transcript)
    Actual_Transcript = data['results']['transcripts'][0]['transcript']
    print("Spoken CMD = " + Actual_Transcript)
    if(Actual_Transcript == "identify."):
        print("Capture Image")
    else:
        print("Do not capture Image")

def capture_audio():
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
    
capture_audio()
upload_file(wav_output_filename, bucket_name)
transcribe_file(wav_output_filename, bucket_name)

#!/usr/bin/env python3

import pygame
import boto3
import os

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
    
    filename="/home/pi/EID_SuperProject/Output_Audio/label.ogg"
    
    resp = polly.synthesize_speech(OutputFormat=format, Text=text, VoiceId=voice)
    
    soundfile = open(filename, 'wb')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()
    play(filename)
    os.remove(filename)
    
speak("Devansh is the object identifieddd")

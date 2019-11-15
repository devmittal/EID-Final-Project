#!/usr/bin/env python3

import pygame
import boto3
import os

def play(filename):
    print("Playing output")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
         pygame.time.Clock().tick(10)

def speak(text, format='ogg_vorbis', voice='Brian'):
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

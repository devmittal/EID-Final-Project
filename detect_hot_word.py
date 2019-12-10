import subprocess
import os
import sys

sys.path.insert(1, '/home/pi/EID_SuperProject/rpi-arm-raspbian-8.0-1.1.1')

import snowboydecoder

def detected_callback():
	print ("Hotword Detected")
	detector.terminate()
 	pro = subprocess.Popen(["./magic_wand.py"]).wait()
 	print("Restarting...")
 	os.execv(sys.executable, ['python'] + sys.argv)

detector = snowboydecoder.HotwordDetector("magic_wand.pmdl", sensitivity=0.5, audio_gain=1)

detector.start(detected_callback)

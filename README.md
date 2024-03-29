# EID Project 6

## Magic Wand

### Team Members

Souvik De

Devansh Mittal

### Notes and Installations Instructions

##### AWS and boto3 Setup
Follow the steps specified [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) in order to install Boto3 and setup your authentication credentials. Copy and paste your AWS access key id, AWS secret access key and AWS session token into ~/.aws/credentials. These keys expire after a certain period of time so keep replacing the credentials file with the up-to-date keys.

##### Creating S3 buckets
Create two S3 buckets named 'eid-superproject' and 'eid-superproject-image' on AWS. Keep default settings. One is to store the voice commands and the other stores the images to be sent to the server pi.

##### Creating SQS queue
Create a fifo queue named 'Magic-Wand.fifo'. Remember to enable content-based deduplication.

##### Microphone
Refer to ["Recording Audio on the Raspberry Pi with Python and a USB Microphone"](https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone) to ensure that the microphone is correctly integrated with the pi. Take note of the index of the USB device and replace it in line 26 of magic_wand.py.  

##### Camera
Raspberry Pi indegeneous libraries are required to integrate the Pi Camera. Refere to [this](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera) for more information on how to integrate the camera with the Pi.

##### Snowboy Hotword Detector
Run the following command

`sudo apt-get install python-pyaudio python-pip libatlas-base-dev portaudio19-dev`

##### Database
Follow the instructions at [MySQL on Raspberry Pi](https://pimylifeup.com/raspberry-pi-mysql/) to install and setup MySQL Server for Raspberry Pi. This link also contains information on how to create a database and user with privillages to access the DB.

Use [pip for python3](https://www.raspberrypi.org/documentation/linux/software/python.md) to install [SQL Connector](https://pynative.com/install-mysql-connector-python/) for Python. This page also contains information on how to use and implement the APIs on python to access your MySQL Database.

Create the following tables to store all spoken commands and objects detected.
```sh
MariaDB [project1db]> CREATE TABLE command( 
>	          received VARCHAR(100) NOT NULL, 
>	          state VARCHAR(10) NOT NULL,
>	          entrytimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
```
```sh
MariaDB [project1db]> CREATE TABLE object( 
>	          label VARCHAR(100) NOT NULL, 
>	          state VARCHAR(10) NOT NULL,
>	          entrytimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

##### Execution Instructions

On the client pi, run

`python detect_hot_word.py`

On the server pi, run

`./server_test.py`

For the website, navigate to [Webclient/index.html](https://github.com/devmittal/EID-Final-Project/tree/master/Webclient).


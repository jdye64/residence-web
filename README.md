Installation

   * sudo apt-get update
   * sudo apt-get install build-essential python-dev python-twisted python-pip
   * sudo pip install virtualenv virtualenvwrapper
   * echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.profile
   * echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile
   * source ~/.profile
   * mkvirtualenv residence
   * pip install crossbar

   FOR RASPBERRY PI DEVICE ONLY
   * pip install rpi.gpio
   * For running as sudo with virtualenv ```sudo /home/pi/.virtualenvs/residence/bin/python RPiGPIOComponent.py```
   
About

The Residence application consists of a single crossbar.io router running to facilitate the interaction with several individual
components in the Residence session.

1) deviceregistry.py - This is a registry of the devices that are current connected to the Residence session. This component serves as the point where things 
like IOS or Android devices can connect and ask for the complete list of devices they may control.
2) rpi.py - This component runs on a Raspberry PI and allows for controlling several functions on the Raspberry PI itself
or other devices connected to the RPi device like a power outlet bank or something else like a camera.
3) RPiWebCamComponent.py - This componenet is used to get images and video from a USB camera attached to the RPi device.
Required packages to use the camera software are ```sudo apt-get install fswebcam``` URL with some documentation can be
found here ```http://www.raspberrypi.org/documentation/usage/webcams/```
4) RPiAudioPlaybackComponent.py - This component is used to playback audio files from a RPi device. The componet will play
the sound using the speakers connected to the RPi device. This could either be 3.5mm headphones speakers or that sound could
go through the HDMI output to play on nicer speakers or through a TV.
Required Software:
* ```sudo apt-get install alsa-utils```
* ```sudo apt-get install mpg321```
* ```sudo modprobe snd_bcm2835```
* ```sudo amixer cset numid=3 1```
* ```mpg123 ./{FileName.mp3}```
* ```aplay ./{FileName.wav}```
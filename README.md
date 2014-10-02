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
   
About

The Residence application consists of a single crossbar.io router running to facilitate the interaction with several individual
components in the Residence session.

1) deviceregistry.py - This is a registry of the devices that are current connected to the Residence session. This component serves as the point where things 
like IOS or Android devices can connect and ask for the complete list of devices they may control.
2) rpi.py - This component runs on a Raspberry PI and allows for controlling several functions on the Raspberry PI itself
or other devices connected to the RPi device like a power outlet bank or something else like a camera.

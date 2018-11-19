## Install
Install dependencies with the following command:
```bash
sudo apt-get update
sudo pip install pyusb
```

## Issues
### Running pyserial (for the arduino) on a VM does not have required permissions
After enabling the usb device in the VirtualBox VM settings, the serial output corresponding to the arduino should be `/dev/ttyACM0`. 

Run the following to gain permission:
`sudo chmod 666 /dev/ttyACM0`

### Running pyusb for the mic on a VM does not have the required permissions
Find the usb address of the mic with the following:
`lsusb`

Then, use the address to gain permission:
`sudo chmod o+rw /dev/bus/usb/001/00<USB ID>`

## Scripts
### main.py
System to drive the motor to the direction of arrival from the mic.

### DOA.py
Prints out direction of arrival of the mic

### ser_motor_control.py
Sends a serial command to the motor to do 1 revolution

## Links
* http://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/
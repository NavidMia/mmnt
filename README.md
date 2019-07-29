# Moment
Autonomous Camera Tracking - [https://medium.com/mmnt](https://medium.com/mmnt)

![poster](./docs/about/poster.png)

# 1. Installation
## 1.1 Jetson Setup
1. Ensure Jetson has [Jetpack](https://developer.nvidia.com/embedded/jetpack) installed for Cuda (using Jetpack 3.3).
    
    For verification, the following should output Cuda release 9.0.
    ```sh
    /usr/local/cuda/bin/nvcc --version
    ```
2. Set up and activate virtual environment for Python 3.
    ```sh
    sudo apt update
    sudo apt install python3-dev python3-pip
    sudo pip3 install -U virtualenv  # system-wide install

    mkdir ~/venvs
    virtualenv --system-site-packages -p python3 ~/venvs/mmnt
    source ~/venvs/mmnt/bin/activate # to activate the virtual environment
    deactivate # to deactivate the virtual environment
    ```

3. Install Tensorflow from a [pre-built wheel](https://github.com/JasonAtNvidia/JetsonTFBuild) (using TF 1.11.0 TRT Pyton 3.5).
    ```sh
    # After downloading the .whl file
    pip install tensorflow-1.11.0-cp35-cp35m-linux_aarch64.whl
    ```

4. [Install OpenCV](https://www.learnopencv.com/install-opencv3-on-ubuntu/) (using OpenCV 3.4.5).

5. Clone [tf-openpose](https://github.com/ildoonet/tf-pose-estimation)

    Follow the install instructions on the readme. The package install flow seemed to work better than the regular install flow.

6. Clone the [MMNT repo](https://github.com/alexanderyshi/mmnt)

7. Setup for mmnt environment
    ```sh
sudo apt-get update
sudo pip install pyusb
sudo pip install pyserial
brew install libusb
    ```
### Links
* https://devtalk.nvidia.com/default/topic/1025356/how-to-capture-and-display-camera-video-with-python-on-jetson-tx2/
* https://gist.github.com/jkjung-avt/86b60a7723b97da19f7bfa3cb7d2690e


## 1.2 Mic Setup
Install dependencies with the following command:
```bash
sudo apt-get update
sudo pip install pyusb
sudo pip install pyserial
brew install libusb
```

### Issues
#### Running pyserial (for the arduino) on a VM does not have required permissions
After enabling the usb device in the VirtualBox VM settings, the serial output corresponding to the arduino should be `/dev/ttyACM0`. 

Run the following to gain permission:
`sudo chmod 666 /dev/ttyACM0`

#### Running pyusb for the mic on a VM does not have the required permissions
Find the usb address of the mic with the following:
`lsusb`

Then, use the address to gain permission:
`sudo chmod o+rw /dev/bus/usb/001/00<USB ID>`

### Links
* http://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/

# 2. Execution
To run the system, simply execute the python main:
```sh
cd ../mmnt/src/
python main.py
```

# Jetson Setup
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


## Other Useful Links
* https://devtalk.nvidia.com/default/topic/1025356/how-to-capture-and-display-camera-video-with-python-on-jetson-tx2/
* https://gist.github.com/jkjung-avt/86b60a7723b97da19f7bfa3cb7d2690e
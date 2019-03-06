# Linux OTG for mmnt

## Goal and Breakdown
* present a usb video stream to a host system by posing the Jetson TX1 as a USB device 
* achieve this by switching from USB master to slave (device) mode with **either g_webcam or FSConfig**
* OTG is only supported at the carrier-board level on the micro A USB, but our only hope to stream is in **BULK** mode (*isochronous, i.e. HIGH FIXED SPEED, isn't supported in HW*)
* 

## TX1 lsusb: 
*Bus 020 Device 001: ID 0955:7020 NVIDIA Linux for Tegra  Serial: 03232161300550c08104*

## [To config Jetson TX1 USB 3.0 port as storage device mode](https://devtalk.nvidia.com/default/topic/952472/jetson-tx1/jtx1_usb_as-device/post/4937794/#4937794):
```sh
1> Modify the kernel following attached patch.
2> Enable Android Gadget:
echo 0 > /sys/class/android_usb/android0/enable 
echo 0955 > /sys/class/android_usb/android0/idVendor 
echo 7E00 > /sys/class/android_usb/android0/idProduct 
echo mass_storage > /sys/class/android_usb/android0/functions 
echo 0 > /sys/class/android_usb/android0/bDeviceClass 
dd if=/dev/zero of=/home/ubuntu/msc.ext4.img bs=1M count=1k 
mkfs.ext4 /home/ubuntu/msc.ext4.img 
echo /home/ubuntu/msc.ext4.img > /sys/class/android_usb/android0/f_mass_storage/lun/file 
echo 1 > /sys/class/android_usb/android0/enable
3> Plug in USB3.0 cable(Swap the TX/RX signal for normal USB3.0 A to A extension cable)
4> Plug in USB2.0 cable(The system need VBUS detect to identify a USB3.0 host connected)
```
## Linux On The Go Notes
### Issues
[TX1 does not support isochronous mode](https://devtalk.nvidia.com/default/topic/1036885/jetson-tx1/tx1-usb-uvc-gadget-troubles/)
[what is isochronous mode?](https://arstechnica.com/civis/viewtopic.php?t=819870)
[TX1 supports bulk mode only](https://devtalk.nvidia.com/default/topic/1014096/how-to-set-tx2-otg-usb-as-device-mode-/)
### TLDR
* [To config Jetson TX1 USB 3.0 port as device mode ](https://devtalk.nvidia.com/default/topic/952472/jetson-tx1/jtx1_usb_as-device/post/4937794/#4937794) - there should be driver support on TX1
* [Stackexchange discussion ](https://raspberrypi.stackexchange.com/questions/51243/how-do-you-configure-the-pi-zero-to-act-as-a-usb-webcam-using-the-plug-in-camera) TAKE TOP COMMENT, also leads to additional documentation
  * [Simple guide for setting up OTG modes on the Raspberry Pi Zero, the fast way!](https://gist.github.com/gbaman/975e2db164b3ca2b51ae11e45e8fd40a)
  * [UVC ConfigFS Gadget configuration tool](https://gist.github.com/kbingham/c39c4cc7c20882a104c08df5206e2f9f)
### Background
* RPi as webcam [(forum discussion) ](https://www.raspberrypi.org/forums/viewtopic.php?t=148361)
  * 2 methods
    * legacy g_webcam
    * modern configfs
  *  [Linux function directories for UVC control](https://github.com/torvalds/linux/blob/master/Documentation/usb/gadget-testing.txt#L656)
  *  [documentation for controlling UVC gadget in Linux function directories](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uvc)
  *  usb_f_uvc.ko :  Linux USB Video Class for camera controls, [Logitech C270 has support](http://www.ideasonboard.org/uvc/)
* Primer on the Kernel API - [linux/usb_gadget.h C API](http://www.linux-usb.org/gadget/)
  * [a driver-based "OTG Controller" on Mini-AB PHY jacks allow dual-role operation](https://www.kernel.org/doc/htmldocs/gadget/otg.html)
* DIFFERENT EXAMPLE [how to set up the Pi Zero as a usb gadget ](http://isticktoit.net/?p=1383)(from RPi as webcam forum link)
* [Linux USB Gadget modules](https://pi.gbaman.info/?p=699) -> g_webcam
# Linux OTG for mmnt

## Goal and Breakdown
* present a usb video stream to a host system by posing the Jetson TX1 as a USB device 
* documentation on this exact use case of TX1 explains that it is not possible from HW
* typically achieve this by switching from USB master to slave (device) mode with **either g_webcam or FSConfig**
   * to my understanding g_webcam is legacy but easier 
* OTG is only supported at the carrier-board level on the micro A USB, but only in **BULK** mode (*isochronous, i.e. HIGH FIXED SPEED, isn't supported in HW*)
    * Can not stream video on this mode, only send still images
    * According to /proc/config.gz, OTG support was enabled when compiled originally
* A script in /opt/nvidia/l4t-usb-device-mode can be used to set OTG mode, but TX1 will refuse to setup uvc due to isochronous USB mode requirement (error in dmesg)
  * [modifying the script for uvc](https://devtalk.nvidia.com/default/topic/1036885/jetson-tx1/tx1-usb-uvc-gadget-troubles/)

* [TK1 DOES support isochronous and is our best bet for a clean solution](https://devtalk.nvidia.com/default/topic/1023155/jetson-tx1/tegra-xudc-endpoint-transfer-mode/post/5209829/)


## TX1 lsusb: 
*Bus 020 Device 001: ID 0955:7020 NVIDIA Linux for Tegra  Serial: 03232161300550c08104*

## Promising leads for guides
* [Length discussion on setting up driver for TK1 - no conclusion](https://devtalk.nvidia.com/default/topic/897531/jetson-tk1/jetson-tk1-behaving-like-an-usb-camera/2)
* [random forum links](https://devtalk.nvidia.com/default/topic/979120/jetson-tx1/how-to-configure-usb-3-0-otg-function/)
* [Theory on how to use ethernet to spoof camera - possible workaround](https://devtalk.nvidia.com/default/topic/1035421/jetson-tx2/webcam-uvc/post/5260975/#5260975)
* [Stackexchange discussion ](https://raspberrypi.stackexchange.com/questions/51243/how-do-you-configure-the-pi-zero-to-act-as-a-usb-webcam-using-the-plug-in-camera) TAKE TOP COMMENT, also leads to additional documentation
  * [Simple guide for setting up OTG modes on the Raspberry Pi Zero, the fast way!](https://gist.github.com/gbaman/975e2db164b3ca2b51ae11e45e8fd40a)
  * [UVC ConfigFS Gadget configuration tool](https://gist.github.com/kbingham/c39c4cc7c20882a104c08df5206e2f9f)
* https://devtalk.nvidia.com/default/topic/979120/jetson-tx1/how-to-configure-usb-3-0-otg-function/
* https://devtalk.nvidia.com/default/topic/1036885/jetson-tx1/tx1-usb-uvc-gadget-troubles/
* https://devtalk.nvidia.com/default/topic/897531/

## Linux On The Go Notes
### Issue with isochronous mode
[TX1 does not support isochronous mode](https://devtalk.nvidia.com/default/topic/1036885/jetson-tx1/tx1-usb-uvc-gadget-troubles/) pt1
[TX1 does not support isochronous mode](https://devtalk.nvidia.com/default/topic/1023155/jetson-tx1/tegra-xudc-endpoint-transfer-mode/post/5209829/) pt2

[what is isochronous mode?](https://arstechnica.com/civis/viewtopic.php?t=819870)

[TX1 supports bulk mode only](https://devtalk.nvidia.com/default/topic/1014096/how-to-set-tx2-otg-usb-as-device-mode-/)

[Other people use bulk mode for streaming in general as a hack](https://linux-usb.vger.kernel.narkive.com/NnVH6MMA/detecting-start-stop-streaming-for-uvc-webcam-with-bulk-transfer-mode)

[The kernel is carrying a set of changes to the UVC gadget driver to make it request bulk endpoints instead of ISOCH](https://devtalk.nvidia.com/default/topic/1038821/tx1-tegra-xudc-controller-error/?offset=8)
### General Info
* [To config Jetson TX1 USB 3.0 port as storage device mode ](https://devtalk.nvidia.com/default/topic/952472/jetson-tx1/jtx1_usb_as-device/post/4937794/#4937794) - this isn't exactly what we want and demands a recompilation of a linux module
* Source: https://developer.nvidia.com/embedded/linux-tegra-r282
* [recompiling linux modules](https://www.proware.com.tw/support/software/cdb16patch-lnx/linux-patch.pdf) - i feel like i might not actually need to do this, maybe the patch is for storage devices only?
* [setup otg](https://wiki.tizen.org/USB/Linux_USB_Layers/Configfs_Composite_Gadget/Usage_eq._to_g_webcam.ko)
### Background
* RPi as webcam [(forum discussion) ](https://www.raspberrypi.org/forums/viewtopic.php?t=148361)
  * 2 methods
    * legacy g_webcam
    * modern configfs
  *  [Linux function directories for UVC control](https://github.com/torvalds/linux/blob/master/Documentation/usb/gadget-testing.txt#L656)
  *  [documentation for controlling UVC gadget in Linux function directories](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uvc)
  *  usb_f_uvc.ko :  Linux USB Video Class for camera controls, [Logitech C270 has support](http://www.ideasonboard.org/uvc/)
     * **this module requires isochronous usb mode but our [hardware does not support it](https://devtalk.nvidia.com/default/topic/1023155/jetson-tx1/tegra-xudc-endpoint-transfer-mode/1)**
* Primer on the Kernel API - [linux/usb_gadget.h C API](http://www.linux-usb.org/gadget/)
  * [a driver-based "OTG Controller" on Mini-AB PHY jacks allow dual-role operation](https://www.kernel.org/doc/htmldocs/gadget/otg.html)
* DIFFERENT EXAMPLE [how to set up the Pi Zero as a usb gadget ](http://isticktoit.net/?p=1383)(from RPi as webcam forum link)
* [Linux USB Gadget modules](https://pi.gbaman.info/?p=699) -> g_webcam
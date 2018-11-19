from tuning import Tuning
import usb.core
import usb.util
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
if dev:
    mic = Tuning(dev)
    mic.write("NONSTATNOISEONOFF", 1)
    mic.write("NONSTATNOISEONOFF", 1)
    while True:
        try:
            print mic.direction
            time.sleep(1)
        except KeyboardInterrupt:
            break

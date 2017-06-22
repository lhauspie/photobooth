import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (2592, 1944)
    time.sleep(2)
    camera.start_preview()
    time.sleep(2)
    camera.exif_tags['IFD0.Artist'] = 'Me!'
    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2013 Me!'
    camera.capture('foo.jpg')
    camera.stop_preview()
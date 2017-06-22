import time
import picamera

with picamera.PiCamera() as camera:
    lesIso = [100, 200, 400, 800, 1600]
    lesBrightness = [60, 70, 80, 90, 100]
    lesContrasts = [0, 25, 50, 75, 100]
    
    camera.resolution = (900, 600)
    camera.start_preview()
    time.sleep(10)
    # camera.preview_alpha = 220
    # camera.exposure_compensation = 2
    # camera.exposure_mode = 'spotlight'
    # camera.meter_mode = 'matrix'
    # camera.image_effect = 'gpen'
    
    for iso in lesIso :
        camera.iso = iso
        for brightness in lesBrightness :
            camera.brightness = brightness
            for contrast in lesContrasts :
                camera.contrast = contrast
                time.sleep(5)
                camera.capture('iso' + str('%04d' % (iso)) + '_brightness' + str('%03d' % (brightness)) + '_contrast' + str('%03d' % (contrast)) + '.jpg')
            
    camera.stop_preview()
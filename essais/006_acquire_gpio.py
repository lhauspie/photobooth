import time
import RPi.GPIO as GPIO


class MyGame:
    def __init__(self):
        self._running = True
        self._surf_display = None
        self.size = self.width, self.height = 150, 150

    def on_init(self):
        self._running = True
        #set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
                
        while (self._running):
            if GPIO.input(17) == 0:
                print "Circuit 17 closed"
            if GPIO.input(17) == 1:
                print "Circuit 17 opened"
            if GPIO.input(27) == 0:
                print "Circuit 27 closed"
            if GPIO.input(27) == 1:
                print "Circuit 27 opened"
            if GPIO.input(22) == 0:
                print "Circuit 22 closed"
            if GPIO.input(22) == 1:
                print "Circuit 22 opened"
            time.sleep(0.5)

if __name__ == "__main__" :
    mygame = MyGame()
    mygame.on_execute()

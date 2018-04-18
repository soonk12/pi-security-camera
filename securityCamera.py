from time import sleep
from datetime import datetime
from picamera import PiCamera

camera = PiCamera()
#camera.resolution = (1024, 768)
camera.rotation = 180
camera.start_preview()
# warm-up
sleep(2)

for x in range(60):
    sleep(15)
    d = datetime.now()
    filename = d.strftime("data/pic_%Y%m%d_%H%M%S.%f.jpg")
    camera.capture(filename)

from time import sleep
from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2

camera = PiCamera()
#camera.resolution = (640, 480)
#camera.rotation = 180
camera.start_preview()
# warm-up
sleep(2)

# inspired from https://github.com/erogol/RaspiSecurity/blob/master/pi_surveillance.py

#for x in range(60):
#    sleep(15)
#    d = datetime.now()
#    filename = d.strftime("data/pic_%Y%m%d_%H%M%S.%f.jpg")
#    camera.capture(filename)

#rawCapture = PiRGBArray(camera, size=(640, 480))
rawCapture = PiRGBArray(camera)
frameCount = 0
avg = None

print "Pi Security Camera Starting"

# capture frames from camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.now()

    # convert to grayscale and blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)

    if avg is None:
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue
        
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    cv2.accumulateWeighted(gray, avg, 0.5)

    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    changed = False
    for c in cnts:
        if cv2.contourArea(c) < 500:
            continue

        #(x,y,w,h) = cv2.boundingRect(c)
        #cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)
        cv2.drawContours(frame, [c], 0, (0, 255, 0), 2)
        changed = True

    if changed: 
        timestamp = datetime.now()
        filename = "frame_{}_{}.jpg".format(timestamp.strftime("%Y%m%d_%H%M%S.%f"), frameCount)
        print "Saving " + filename
        cv2.imwrite("/home/pi/pisec/data/frame_{}_{}.jpg".format(timestamp.strftime("%Y%m%d_%H%M%S.%f"), frameCount), frame)
       
    frameCount += 1
    rawCapture.truncate(0)
    

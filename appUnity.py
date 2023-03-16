import cv2
import numpy as np
import math
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5065
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hsvValue = np.load('hsv.npy')  # load the hsv preset create from ColorPicker
capture = cv2.VideoCapture(0)
capture.set(3, 1280)
capture.set(4, 720)
capture.set(10, 150)
kernel = np.ones((5, 5), np.uint8)
switch = 'out'

backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
background_threshold = 600

noiseth = 200
canvas = None
x, y = 0, 0

myColorValues = [[255, 0, 0], [0, 165, 255], [0, 0, 255], [255, 255, 255]]  # color for changing

# colors = [(255, 0, 0), (0, 165, 255),
#           (0, 0, 255), (0, 0, 0)]

selectedColor = 1  # default
colorNames = ["Blue", "Orange", "Red", "White"]

lineThick = 4
center = [0, 0]  # default center value
imgcounter = 0


def findColor(frame, hsvValue, myColorValues):
    framehsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    global x, y

    lower = np.array(hsvValue[0])
    upper = np.array(hsvValue[1])
    mask = cv2.inRange(framehsv, lower, upper)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=3)
    x1, y1 = getContours(mask)  # detect the contour and return contour coordinate



    # The drawing function will draw a line from 2 point
    if x == 0 and y == 0:  # if the pen is not inside the canvas or first start the app
        x, y = x1, y1  # pass the current coordinate of the pen
        mess = str(x1) + "," + str(y1)
    else:  # draw a line from previous frame location of the pen to current frame position
        cv2.line(canvas, (x, y), (x1, y1), myColorValues[selectedColor], lineThick)
        x, y = x1, y1  # after drawing, the current position become previous position
        mess = str(x1) + "," + str(y1)

    sock.sendto(mess.encode(), (UDP_IP, UDP_PORT))
    # cv2.circle(frameResult, (x1, y1), 10, myColorValues[selectedColor], cv2.FILLED)  # draw the tip
    # cv2.putText(frameResult, colorNames[selectedColor], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, myColorValues[selectedColor], thickness=2)

    cv2.imshow("Masking", mask)


def getContours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x2, y2, w, h = 0, 0, 0, 0
    global center, x, y

    # if contours dectected and exceed the noise(white space) thresh hold:
    if contours and cv2.contourArea(max(contours, key=cv2.contourArea)) > noiseth:
        c = max(contours, key=cv2.contourArea)  # get the largest contour
        M = cv2.moments(c)  # calculate the position of the contour on screen
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
        x2, y2, w, h = cv2.boundingRect(c)
        cv2.rectangle(frameResult, (x2, y2), (x2 + w, y2 + h), myColorValues[selectedColor], 2)  # draw box
    else:
        x, y = 0, 0  # if no contour detected

    return x2, y2  # current position


def createbutton(frame):
    # on top of the screen from left to right
    frame = cv2.rectangle(frame, (40, 1), (140, 65), (122, 122, 122), -1)  # clear button
    frame = cv2.rectangle(frame, (160, 1), (255, 65), myColorValues[0], -1)  # button 2
    frame = cv2.rectangle(frame, (275, 1), (370, 65), myColorValues[1], -1)  # button 3
    frame = cv2.rectangle(frame, (390, 1), (485, 65), myColorValues[2], -1)  # button 4
    frame = cv2.rectangle(frame, (505, 1), (600, 65), myColorValues[3], -1)  # button 5
    frame = cv2.rectangle(frame, (735, 1), (830, 65), (0, 0, 0), -1)  # button 5
    frame = cv2.circle(frame, (780, 20), lineThick, myColorValues[selectedColor], cv2.FILLED)
    cv2.putText(frame, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "BLUE", (185, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, "ORANGE", (298, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, "RED", (420, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, "WHITE", (520, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 0, 0), 2, cv2.LINE_AA)


# check if the position of the pen is in range
def checkbutton(center):
    global canvas
    global selectedColor, lineThick, switch
    if (center[1] <= 100):
        if (40 <= center[0] <= 170):  # if the center value matched, re-initialize the points list
            canvas = None
        elif (180 <= center[0] <= 250):
            selectedColor = 0
        elif (270 <= center[0] <= 360):
            selectedColor = 1
        elif (390 <= center[0] <= 480):
            selectedColor = 2
        elif (520 <= center[0] <= 680):
            selectedColor = 3
        elif (730 <= center[0] <= 830):
            if lineThick == 4 and switch == 'out':
                switch = 'in'
                lineThick = 15

            if lineThick == 15 and switch == 'out':
                lineThick = 4
                switch = 'in'
    else:
        switch = 'out'


# Main program
while True:

    isTrue, frame = capture.read()
    frame = cv2.flip(frame, 1)

    # createbutton(frame)

    if canvas is None:
        canvas = np.zeros_like(frame)  # blank canvas
    frameResult = frame.copy()

    findColor(frame, hsvValue, myColorValues)  # track and draw
    frameResult = cv2.add(frameResult, canvas)
    # checkbutton(center)
    cv2.imshow("Test", frameResult)
    k = cv2.waitKey(33)
    if k == 27:  # press ESC to quit
        break
    elif k == 32:  # press SPACE to take picture
        img_name = "opencv_frame_{}.png".format(imgcounter)
        cv2.imwrite(img_name, frameResult)
        print("{} written!".format(img_name))
        img = cv2.imread("{}".format(img_name))
        cv2.imshow("Screenshot", img)
        imgcounter += 1

capture.release()
cv2.destroyAllWindows()

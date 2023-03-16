import cv2
import numpy as np

hsvValue = np.load('hsv.npy')  # load the hsv preset create from ColorPicker
capture = cv2.VideoCapture(0)
capture.set(3, 1280)
capture.set(4, 720)
capture.set(10, 150)
kernel = np.ones((5, 5), np.uint8)

pen_img = cv2.resize(cv2.imread('pen.png', 1), (50, 50))
eraser_img = cv2.resize(cv2.imread('eraser.png', 1), (50, 50))

switch = 'out'
switch_pe = 'pen'

noiseth = 50
canvas = None
x, y = 0, 0
center = [0, 0]  # default center value

myColorValues = [[255, 0, 0], [0, 165, 255], [0, 0, 255], [255, 255, 255]]  # color for changing
colorNames = ["Blue", "Orange", "Red", "White"]
selectedColor = 1  # default

lineThick = 4
imgcounter = 0


def getContours(frame):
    contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x2, y2, w, h = 0, 0, 0, 0
    global center, x, y

    # if contours detected and exceed the noise(white space) thresh hold:
    if contours and cv2.contourArea(max(contours, key=cv2.contourArea)) > noiseth:
        c = max(contours, key=cv2.contourArea)  # get the largest contour
        M = cv2.moments(c)  # calculate the position of the contour on screen
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
        x2, y2, w, h = cv2.boundingRect(c)
        cv2.rectangle(frameResult, (x2, y2), (x2 + w, y2 + h), myColorValues[selectedColor], 2)  # draw box
    else:
        x, y = 0, 0  # if no contour detected

    return x2, y2  # current position


def findColor(frame, hsvValue, myColorValues):
    framehsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    global x, y
    lower = np.array(hsvValue[0])
    upper = np.array(hsvValue[1])
    mask = cv2.inRange(framehsv, lower, upper)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    x1, y1 = getContours(mask)  # detect the contour and return contour coordinate

    # The drawing function will draw a line from 2 point
    if x == 0 and y == 0:  # if the pen is not inside the canvas or first start the app
        x, y = x1, y1  # pass the current coordinate of the pen
    else:  # draw a line from previous frame location of the pen to current frame position
        if switch_pe == 'pen':
            cv2.line(canvas, (x, y), (x1, y1), myColorValues[selectedColor], lineThick)
            x, y = x1, y1  # after drawing, the current position become previous position
        else:
            cv2.circle(frameResult, (x1, y1), 20, (255, 255, 255), -1)
            cv2.circle(canvas, (x1, y1), 20, (0, 0, 0), -1)
            x, y = x1, y1  # after drawing, the current position become previous position




def checkbutton(center):
    global canvas
    global selectedColor, lineThick, switch, switch_pe
    if center[1] <= 100:
        if 40 <= center[0] <= 170:  # if the center value matched, re-initialize the points list
            canvas = None
        elif 180 <= center[0] <= 250:
            selectedColor = 0
        elif 270 <= center[0] <= 360:
            selectedColor = 1
        elif 390 <= center[0] <= 480:
            selectedColor = 2
        elif 520 <= center[0] <= 680:
            selectedColor = 3
        elif 730 <= center[0] <= 830:
            if lineThick == 4 and switch == 'out':
                switch = 'in'
                lineThick = 15

            if lineThick == 15 and switch == 'out':
                lineThick = 4
                switch = 'in'
        elif 1000 <= center[0] <= 1050:
            if switch_pe == 'pen' and switch == 'out':
                switch = 'in'
                switch_pe = 'eraser'

            if switch_pe == 'eraser' and switch == 'out':
                switch_pe = 'pen'
                switch = 'in'
    else:
        switch = 'out'


# Main program
def createbutton(image):
    # on top of the screen from left to right
    image = cv2.rectangle(image, (40, 1), (140, 65), (122, 122, 122), -1)  # clear button with black border
    image = cv2.rectangle(image, (40, 1), (140, 65), (255, 255, 255), 3)

    image = cv2.rectangle(image, (160, 1), (255, 65), myColorValues[0], -1)  # button 2
    if selectedColor == 0:  # create black border around if selected
        image = cv2.rectangle(image, (160, 1), (255, 65), (0, 0, 0), 5)

    image = cv2.rectangle(image, (275, 1), (370, 65), myColorValues[1], -1)  # button 3
    if selectedColor == 1:
        image = cv2.rectangle(image, (275, 1), (370, 65), (0, 0, 0), 5)

    image = cv2.rectangle(image, (390, 1), (485, 65), myColorValues[2], -1)  # button 4
    if selectedColor == 2:
        image = cv2.rectangle(image, (390, 1), (485, 65), (0, 0, 0), 5)

    image = cv2.rectangle(image, (505, 1), (600, 65), myColorValues[3], -1)  # button 5
    if selectedColor == 3:
        image = cv2.rectangle(image, (505, 1), (600, 65), (0, 0, 0), 5)

    image = cv2.rectangle(image, (735, 1), (830, 65), (0, 0, 0), -1)  # button 6
    # frame = cv2.rectangle(frame, (965, 1), (1060, 65), (255, 255, 255), -1)  # button 7

    if switch_pe == 'pen':  # change the icon depend on selected mode
        image[0: 50, 1000: 1050] = pen_img
        image = cv2.rectangle(image, (1000, 0), (1050, 50), (0, 0, 0), 3)
    else:
        image[0: 50, 1000: 1050] = eraser_img
        image = cv2.rectangle(image, (1000, 0), (1050, 50), (0, 0, 0), 3)

    image = cv2.circle(image, (780, 20), lineThick, myColorValues[selectedColor], cv2.FILLED)
    cv2.putText(image, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    # cv2.putText(frame, "BLUE", (185, 33),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (255, 255, 255), 2, cv2.LINE_AA)
    #
    # cv2.putText(frame, "ORANGE", (298, 33),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (255, 255, 255), 2, cv2.LINE_AA)
    #
    # cv2.putText(frame, "RED", (420, 33),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (255, 255, 255), 2, cv2.LINE_AA)
    #
    # cv2.putText(frame, "WHITE", (520, 33),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (0, 0, 0), 2, cv2.LINE_AA)


while True:

    isTrue, frame = capture.read()
    frame = cv2.flip(frame, 1)

    createbutton(frame)

    if canvas is None:
        canvas = np.zeros_like(frame)  # blank canvas

    frameResult = frame.copy()
    findColor(frame, hsvValue, myColorValues)  # track and draw

    _, mask = cv2.threshold(cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY), 20, 255, cv2.THRESH_BINARY)
    foreground = cv2.bitwise_and(canvas, canvas, mask=mask)
    background = cv2.bitwise_and(frameResult, frameResult, mask=cv2.bitwise_not(mask))
    frameResult = cv2.add(foreground, background)
    frameResult = cv2.add(frameResult, canvas)  # Merge the canvas to the frame

    checkbutton(center)

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




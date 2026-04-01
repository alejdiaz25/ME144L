# read_video_contour_v1.py
# ME 144L DSC Lab
# Includes user defined ROI
import cv2
import numpy as np
import statistics
import matplotlib.pyplot as plt
import pandas as pd
import math

ccoord = [] # list for holding the (x,y) coordinates of object
x, y = [], []
t1, t2, t3, t4 = [], [], [], []
fn = []

# function to detect mouse click, find (x,y)
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        vcoord.append((x, y))
        print(f"Clicked at: ({x}, {y})")
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1) # Mark the clicked point
        cv2.imshow('image', img)

# open video
video_path = 'moving_object_with_ruler_x.mp4'
df = pd.read_csv('moving_object_with_ruler_x.csv') # data with time stamps
ruler_length = 9.5 # inches of cropped width for #6
mytime = df.iloc[:,0]

cap = cv2.VideoCapture(video_path)
FPS = cap.get(cv2.CAP_PROP_FPS) # frame rate
print(f"Frame rate is {FPS:.1f} Hz")

# to use a webcam use this line instead
# you might need to change the number 0 to 1 or 2
#cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Find crop image coordinates once using select ROI
# then apply each time
#-------------------------------------------------------------------------
# Option for manual ROI selected cropping
# Display the frame number you want (optional)
frame_number = 30
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
ret, frame = cap.read()
# Check if frame was read successfully
if ret:
    # cv2.imshow('First Frame', frame)
    image = frame
    # Select ROI
    roi = cv2.selectROI("Select ROI", image)
    # Print ROI coordinates to test (optional)
    # print(roi)
    # Crop the ROI, call that new image cropped_frame
    cropped_frame = frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    #cv2.imshow('Cropped Image using ROI', cropped_image)
else:
    print("Error: Could not read the first frame.")

#-------------------------------------------------------------------------

# iterate through video frames to identify the centers
print("Working through frames, showing largest contour only...")
i=0
while True:
    #check if frames can be read
    ret, frame = cap.read()
    if not ret:
        break

    # Crop the frame based on selected ROI
    cropped_frame = frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

    # convert frame to grayscale so you can identify white areas (the needle bob)
    gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)

    # threshold to get white areas
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
    # threshold to get black areas
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # check if there are contours detected
    # if so, find the largest and drawContours, red dot at center

    if contours:
        # get largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        # note: in max() you use key to define a function to extract a comparison key for each
        # element in contours 
        # cv2.contourArea(contour) gives you the number of pixels enclosed by a contour
        
        cv2.drawContours(cropped_frame, largest_contour, -1, (0, 255, 0), 2)

        # fit minimum enclosing circle to the contour
        # if you dont add this and take the centerpoint of the contour
        # the centerpoint will deviate because of the small changes in depicted pixels
        # between images
        (xc, yc), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(xc), int(yc))
        ccoord.append((xc, yc))
        radius = int(radius)
        # time based on FPS
        t1.append(i/FPS)
        # time based using MSEC info
        t2.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
        # time also recorded as mytime during capture
        # time based on frame number
        fn.append(cap.get(cv2.CAP_PROP_POS_FRAMES))
        x.append(xc)
        y.append(yc)

        i += 1

        # draw the circle
        cv2.circle(cropped_frame, center, radius, (255, 0, 0), 2)
        # draw the center
        cv2.circle(cropped_frame, center, 3, (0, 0, 255), -1)

    # show image
    cv2.imshow('Fitted Circle on Contour', cropped_frame)

    if cv2.waitKey(50) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

print(len(x))
print(len(fn))
print(len(mytime))
height, width, _ = cropped_frame.shape
scale = ruler_length/width # put in the scale using ruler
print(f"Area of largest contour is {cv2.contourArea(largest_contour):.1f} pixels")
print(f"Perimeter of largest contour is {cv2.arcLength(largest_contour, True):.1f} pixels")

plt.rcParams["figure.figsize"] = [5, 4]
plt.rcParams["figure.autolayout"] = True
# To create an nx1 of subplots
fig, (ax1, ax2) = plt.subplots(2)
ax1.plot([scale*(xi) for xi in x],[scale*(height-yi) for yi in y],'ko')
ax1.set_xlabel('x, inches')
ax1.set_ylabel('y, inches')

# adjust time since we skip up to frame_number
# option 1, just use FPS = constant, shift by constant FPS
# option 2, use MSEC, shift by constant FPS
# option 3, use mytime recorded, shift by measured shift
print(mytime[int(frame_number)])
for j in range(len(x)):
    t3.append(mytime[int(frame_number)+j]-mytime[int(frame_number)])
    t4.append(int(fn[j]-frame_number)/FPS)

ax2.plot([(ti) for ti in t1],[scale*(xi) for xi in x],'k.', label="Constant FPS")
ax2.plot([(ti-frame_number/FPS) for ti in t2],[scale*(xi) for xi in x],'g.', label="Using MSEC")
ax2.plot(t3,[scale*(xi) for xi in x],'b.', label="Using time()")
ax2.plot(t4,[scale*(xi) for xi in x],'r.', label="Using frame number")
ax2.legend(loc="lower right")

ax2.set_ylabel('x, inches')
ax2.set_xlabel('Time, sec')
plt.show()

# while True:
#     # now get vertex coordinates interactively by mouse click
#     # the last image is in gray (could use cropped_frame?)
#     img = gray
#     cv2.imshow('image', img)
#     cv2.setMouseCallback('image', click_event)

#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         break

cap.release()
cv2.destroyAllWindows()



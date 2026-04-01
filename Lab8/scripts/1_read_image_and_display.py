# 1_read_image_and_display.py
# ME 144L DSCLab, Spring 2026

import cv2 as cv

# read in image
img_o = cv.imread('images/Alu.jpg')

height, width, channels = img_o.shape
# channels is for color images
print("Height:", height)
print("Width:", width)
print("Channels:", channels)

# Use the cvtColor() function to grayscale the image
img = cv.cvtColor(img_o, cv.COLOR_BGR2GRAY)
height, width = img.shape
# channels is for color images
print("Height:", height)
print("Width:", width)
print("Hit any key to close window")

cv.imshow('example', img)
# Hit any key on the keyboard to close the window
cv.waitKey(0)

cv.destroyAllWindows()

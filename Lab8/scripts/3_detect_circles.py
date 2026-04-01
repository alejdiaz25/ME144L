import cv2
import numpy as np

print("When image appears, note the identified objects (highlighted in green)")
print("Make sure the window is active, then press any key to end")


# Read the image
image = cv2.imread('images/example_two_positions.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Blur the image to reduce noise
# blurred = cv2.medianBlur(gray, 5)

# Detect circles using Hough Circle Transform
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                           param1=50, param2=30, minRadius=0, maxRadius=0)

# Draw the detected circles
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])
        radius = i[2]
        cv2.circle(image, center, radius, (0, 255, 0), 2)
        print(center)

# Display the image and coordinates
cv2.imshow('Automatically detected objects', image)
cv2.waitKey(0) # press key to close windows
cv2.destroyAllWindows()

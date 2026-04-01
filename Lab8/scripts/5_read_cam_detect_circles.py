import cv2
import numpy as np

# Open the camera (usually 0 for the default camera)
cap = cv2.VideoCapture(0)
# 0 = external USB, if connected
# 1 = internal

while True:
    # Read the frame from the camera
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        break

    # Display the frame
    cv2.imshow("Camera", frame)

    # Check if the user pressed 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()


# Now use the frame as your image, make it gray
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# the rest is just pasted from the last code
# Blur the image to reduce noise
gray = cv2.medianBlur(gray, 5)

# Detect circles using Hough Circle Transform
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10,
                           param1=50, param2=40, minRadius=0, maxRadius=0)

# Draw the detected circles
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])
        radius = i[2]
        cv2.circle(frame, center, radius, (0, 255, 0), 2)
        print(center)

# Display the image and coordinates
cv2.imshow('Detected Circles', frame)
cv2.waitKey(0) # press key to close windows






cv2.destroyAllWindows()
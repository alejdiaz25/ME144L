import cv2

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

# Save the captured frame to a file
# cv2.imwrite('captured_image.jpg', frame)

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()


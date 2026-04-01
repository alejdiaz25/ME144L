# Read camera and save videos to file
# ME 144L DSCLab, Spring 2025; updated Summer 2025
# Default setting is to save a collected video to file 'output.mp4'
# For successive tests, make sure to 
# When the program is run, video collection begins and stops when user presses 'q'
import cv2
import time
import csv

# Open the default camera (camera index 0)
cap = cv2.VideoCapture(0)

filename = 'moving_object_with_ruler_x.mp4'
time_file = 'moving_object_with_ruler_x.csv' # saves time stamps using time.time()
#filename = 'output.mp4'

prev_frame_time = 0
new_frame_time = 0
t = []

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()


# Get the width and height of the frames
# needed for saving video
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define a codec and create a VideoWriter object
# FourCC code for MP4:
# - 'mp4v' (MPEG-4)
# NOTE: you can also use other video file codecs. See help for VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Create VideoWriter object to save the output video
out = cv2.VideoWriter(filename, fourcc, 30.0, (frame_width, frame_height))

t0 = time.time()
print("t0 = ", t0)
i = 0
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if ret:
        # Write the frame to the output file
        out.write(frame)
        # record time stamps
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        t.append(new_frame_time - t0)
        i += 1

        # Display the resulting frame (optional)
        cv2.imshow('Camera Feed', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

print(i)
with open(time_file, "w") as file:
    for number in t:
        file.write(str(number) + "\n")

# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()
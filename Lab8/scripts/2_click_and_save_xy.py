import cv2

coordinates = [] # define a list to save coordinates

print("When image appears, click the center of the three circular objects, then press q")
print("Press q when done")

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinates.append((x, y))
        print(f"Clicked at: ({x}, {y})")
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1) # Mark the clicked point
        cv2.imshow('image', img)

img = cv2.imread('images/example_two_positions.jpg')
#img = cv2.imread('images/part_2.jpg')
cv2.imshow('image', img)

cv2.setMouseCallback('image', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()

print("Saved coordinates:", coordinates)

# === Compute angle at vertex ===
import numpy as np

ref = np.array(coordinates[0])
vertex = np.array(coordinates[1])
pos = np.array(coordinates[2])

v1 = ref - vertex
v2 = pos - vertex

# Compute angle
dot = np.dot(v1, v2)
norm_v1 = np.linalg.norm(v1)
norm_v2 = np.linalg.norm(v2)

angle_rad = np.arccos(dot / (norm_v1 * norm_v2))
angle_deg = np.degrees(angle_rad)

print(f"\nAngle at vertex: {angle_deg:.2f} degrees")
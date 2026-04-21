"""
generate_lab8_figures.py
Generates trajectory_xy.png and x_vs_time.png for the Lab 8 report.
Uses the full video frame as ROI (no interactive selectROI).
Saves figures to ../figures/ relative to this script.
"""

import os
import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-interactive backend so no GUI window opens
import matplotlib.pyplot as plt

# Paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAB8_DIR = os.path.dirname(SCRIPT_DIR)
VIDEO_PATH = os.path.join(LAB8_DIR, 'data', 'moving_object_with_ruler_x.mp4')
CSV_PATH = os.path.join(LAB8_DIR, 'data', 'moving_object_with_ruler_x.csv')
FIGURES_DIR = os.path.join(LAB8_DIR, 'figures')

ruler_length = 9.5  # inches (matches script 8)
frame_number = 30   # starting frame (matches script 8)

# Load timestamps
df = pd.read_csv(CSV_PATH, header=None)
mytime = df.iloc[:, 0]

cap = cv2.VideoCapture(VIDEO_PATH)
FPS = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Frame rate: {FPS:.1f} Hz,  Frame size: {frame_width}x{frame_height}")

# Use the full frame as ROI (x, y, w, h)
roi = (0, 0, frame_width, frame_height)

# Skip to frame_number
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

ccoord = []
x, y = [], []
t1, t2, t3, t4 = [], [], [], []
fn = []

i = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Crop to ROI
    cropped_frame = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]

    # Grayscale
    gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)

    # Threshold: inverted binary to find dark object (matches script 8 effective threshold)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (xc, yc), radius = cv2.minEnclosingCircle(largest_contour)

        ccoord.append((xc, yc))
        t1.append(i / FPS)
        t2.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
        fn.append(cap.get(cv2.CAP_PROP_POS_FRAMES))
        x.append(xc)
        y.append(yc)
        i += 1

cap.release()
print(f"Tracked {len(x)} frames")

height = roi[3]
width = roi[2]
scale = ruler_length / width  # inches per pixel

# Build t3 and t4 (matching script 8 logic)
for j in range(len(x)):
    t3.append(mytime[int(frame_number) + j] - mytime[int(frame_number)])
    t4.append(int(fn[j] - frame_number) / FPS)

# --- Figure 1: x vs y trajectory ---
plt.rcParams["figure.figsize"] = [5, 4]
plt.rcParams["figure.autolayout"] = True
fig1, ax1 = plt.subplots()
ax1.plot([scale * xi for xi in x], [scale * (height - yi) for yi in y], 'ko', markersize=2)
ax1.set_xlabel('x, inches')
ax1.set_ylabel('y, inches')
ax1.set_title('Object Trajectory (x vs. y)')
fig1.savefig(os.path.join(FIGURES_DIR, 'trajectory_xy.png'), dpi=150, bbox_inches='tight')
plt.close(fig1)
print("Saved trajectory_xy.png")

# --- Figure 2: x vs time (four methods) ---
fig2, ax2 = plt.subplots(figsize=[6, 4])
ax2.plot(t1, [scale * xi for xi in x], 'k.', markersize=3, label='Constant FPS')
ax2.plot([(ti - frame_number / FPS) for ti in t2], [scale * xi for xi in x], 'g.', markersize=3, label='Using MSEC')
ax2.plot(t3, [scale * xi for xi in x], 'b.', markersize=3, label='Using time()')
ax2.plot(t4, [scale * xi for xi in x], 'r.', markersize=3, label='Using frame number')
ax2.legend(loc='lower right', fontsize=8)
ax2.set_ylabel('x, inches')
ax2.set_xlabel('Time, sec')
ax2.set_title('x Position vs. Time (Four Timing Methods)')
plt.tight_layout()
fig2.savefig(os.path.join(FIGURES_DIR, 'x_vs_time.png'), dpi=150, bbox_inches='tight')
plt.close(fig2)
print("Saved x_vs_time.png")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.close('all')
filename = 'test1771963952.csv'
data = pd.read_csv(filename)

time = np.array(data.Time)
x = np.array(data.accX) # [counts]
y = np.array(data.accY) # [counts]
z = np.array(data.accZ) # [counts]
wx = np.array(data.wx)  # [counts]
wy = np.array(data.wy)  # [counts]
wz = np.array(data.wz)  # [counts]

# convert counts to gs
conv_accel = 0.244e-3 # 2g range; convert from int to float in [g]
# NOTE: 0.061 for 2g, 0.122 for 4g, 0.244 for 8g, 0.488 for 16g
accx_g = conv_accel*x   # [g]
accy_g = conv_accel*y   # [g] 
accz_g = conv_accel*z  # [g]

conv_gyro =  4.375e-3   #  125 dps range; convert from int to float in [dps]
# NOTE: 4.375 for 125 dps, 8.75 for 250, 17.50 for 500, 35 for 1000, 70 for 2000
wx_dps = conv_gyro*wx   # [dps]
wy_dps = conv_gyro*wy   # [dps]
wz_dps = conv_gyro*wz   # [dps]

plt.figure(figsize=(12,5))
plt.plot(time, accx_g, label='x')
plt.plot(time, accy_g, label='y')
plt.plot(time, accz_g, label='z')
plt.grid()
plt.legend()
plt.xlabel('Time [s]')
plt.ylabel("Acceleration [g]")
plt.title("Acceleration vs Time")

plt.figure(figsize=(12,5))
plt.plot(time, wx_dps, label='wx')
plt.plot(time, wy_dps, label='wy')
plt.plot(time, wz_dps, label='wz')
plt.grid()
plt.legend()
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [deg/sec]')
plt.title('Gyro Data vs Time')
plt.show()

# Calculate Accelerometer mean and sd
mean_accx = np.mean(accx_g)
std_accx = np.std(accx_g, ddof=1)
print(f"AccX: Mean = {mean_accx:.3f} g, Std Dev = {std_accx:.3f} g")

mean_accy = np.mean(accy_g)
std_accy = np.std(accy_g, ddof=1)
print(f"AccY: Mean = {mean_accy:.3f} g, Std Dev = {std_accy:.3f} g")

mean_accz = np.mean(accz_g)
std_accz = np.std(accz_g, ddof=1)
print(f"AccZ: Mean = {mean_accz:.3f} g, Std Dev = {std_accz:.3f} g")


# Calculate Gyro mean and sd
mean_wx = np.mean(wx_dps)
std_wx = np.std(wx_dps, ddof=1)
print(f"GyroX: Mean = {mean_wx:.3f} dps, Std Dev = {std_wx:.3f} dps")

mean_wy = np.mean(wy_dps)
std_wy = np.std(wy_dps, ddof=1)
print(f"GyroY: Mean = {mean_wy:.3f} dps, Std Dev = {std_wy:.3f} dps")

mean_wz = np.mean(wz_dps)
std_wz = np.std(wz_dps, ddof=1)
print(f"GyroZ: Mean = {mean_wz:.3f} dps, Std Dev = {std_wz:.3f} dps")
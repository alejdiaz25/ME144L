print("Testing installation of pyserial module...")

try:
    import serial
    print("Congratulations, pyserial is installed correctly!")
except:
    print("Error, pyserial is not installed.")

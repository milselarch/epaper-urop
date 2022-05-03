import serial
import time


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.flush()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().rstrip()
            line = line.decode('utf-8')
            print(line)
        else:
           time.sleep(0.1)
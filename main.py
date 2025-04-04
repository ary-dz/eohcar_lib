import serial
import time 
import cv2
import numpy as np
import lane_following
import sys
import os

SERIAL_BAUDRATE = 9600

args = sys.argv
if len(args) > 1:
    if args[1] == "manual":
        manual_mode = True
    elif args[1] == "auto":
        manual_mode = False

if __name__ == "__main__":
    teensy = serial.Serial("/dev/tty.usbmodem119100801")
    teensy.baudrate = SERIAL_BAUDRATE
    time.sleep(1)
    
    send_msg = "ss" # UTF and ASCII are the same for these so this shouldn't matter
    cap = cv2.VideoCapture("http://172.16.115.30:5000/camera")
    while 1:
        try:
            if manual_mode:
                send_msg = input("Desired State: ")
                teensy.write(send_msg.encode("utf-8"))
                print(f"wrote {send_msg}")
                continue
            else:
                #Read image
                ret, frame = cap.read()
                if not ret:
                    break
                
                steering_command, velocity_command, poly_fit = lane_following.get_controls(frame)
            
                print(f"Steering Command: {steering_command:.2f}")
                print(f"Velocity Command: {velocity_command:.2f}")
            
                if velocity_command > 0:
                    speed_state = "f"
                elif velocity_command < 0:
                    speed_state = "b"
                    
                if abs(steering_command) < 0.5:
                    steering_state = "s"
                elif steering_command < -0.5:
                    steering_state = "l"
                else:
                    steering_state = "r"    
                
                
                send_msg = f"{speed_state}{steering_state}"
                print(f"Sending: {send_msg}")
                teensy.write(send_msg.encode("utf-8"))
                print(f"wrote {send_msg}")
                send_msg = f"ss"
                print(f"Sending: {send_msg}")
                teensy.write(send_msg.encode("utf-8"))
                print(f"wrote {send_msg}")
        except KeyboardInterrupt:
            send_msg = f"ss"
            print(f"Sending Shutdown: {send_msg}")
            teensy.write(send_msg.encode("utf-8"))
            print(f"wrote {send_msg}")
            exit()
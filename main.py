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

def opposite(command):
    c= ""
    if command[0]== "s":
        c += "s"
    elif command[0] == "f":
        c += "b"
    elif command[0] == "b":
        c +="f"
    if command[1] == "l":
        c += "r"
    elif command[1] == "r":
        c += "l"
    else:
        c += "s"
    return c
    

if __name__ == "__main__":
    teensy = serial.Serial("/dev/tty.usbmodem119100801")
    teensy.baudrate = SERIAL_BAUDRATE
    time.sleep(1)
    
    send_msg = "ss" # UTF and ASCII are the same for these so this shouldn't matter
    cap = cv2.VideoCapture("http://172.16.115.30:5000/camera")
    previous_command = "ss"
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
                    
                if abs(steering_command) < 0.5:
                    steering_state = "s"
                elif steering_command < -0.5:
                    steering_state = "l"
                else:
                    steering_state = "r"    
                
                if poly_fit is not None:
                    send_msg = f"{speed_state}{steering_state}"
                else:
                    send_msg = opposite(previous_command)
                print(f"Sending: {send_msg}")
                teensy.write(send_msg.encode("utf-8"))
                print(f"wrote {send_msg}")
                previous_command = send_msg
        except KeyboardInterrupt:
            send_msg = f"ss"
            print(f"Sending Shutdown: {send_msg}")
            teensy.write(send_msg.encode("utf-8"))
            print(f"wrote {send_msg}")
            exit()
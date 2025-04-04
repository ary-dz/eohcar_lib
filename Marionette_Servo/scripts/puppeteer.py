import serial
import time 

SERIAL_BAUDRATE = 9600

if __name__ == "__main__":
    teensy = serial.Serial("/dev/tty.usbmodem119100801")
    teensy.baudrate = SERIAL_BAUDRATE
    time.sleep(1)

    send_msg = "ss" # UTF and ASCII are the same for these so this shouldn't matter
    teensy.write(send_msg.encode("utf-8"))
    tap_duration = 0.2
    delay = 0.2
    while 1:
        # send_msg = "fl"
        # teensy.write(send_msg.encode("utf-8"))
        # print(f"wrote {send_msg}")
        # time.sleep(2)

        # send_msg = "br"
        # teensy.write(send_msg.encode("utf-8"))
        # print(f"wrote {send_msg}")
        # time.sleep(2)

        # send_msg = "ss"
        # teensy.write(send_msg.encode("utf-8"))
        # print(f"wrote {send_msg}")
        # time.sleep(2)
        
        # User input version
        send_msg = input("Desired State: ")
        # send_msg = "fr"
        teensy.write(send_msg.encode("utf-8"))
        # time.sleep(tap_duration)
        # send_msg = "ss"
        # teensy.write(send_msg.encode("utf-8"))
        # time.sleep(delay)
        # print(f"wrote {send_msg}")
        # time.sleep(2)



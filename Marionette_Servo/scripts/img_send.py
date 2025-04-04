from picamera2 import Picamera2
import cv2
import socket
import pickle
import struct

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8485))  # Change port if needed
server_socket.listen(1)
conn, addr = server_socket.accept()

while True:
    frame = picam2.capture_array()
    
    # Convert frame to BGR (Picamera2 outputs RGB by default)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Encode frame
    data = pickle.dumps(frame)
    conn.sendall(struct.pack("L", len(data)) + data)

conn.close()
server_socket.close()

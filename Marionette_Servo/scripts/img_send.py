import cv2
import socket
import pickle
import struct

# Initialize camera
cap = cv2.VideoCapture(0)

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8485))  # Change port if needed
server_socket.listen(1)
conn, addr = server_socket.accept()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Encode frame
    data = pickle.dumps(frame)
    conn.sendall(struct.pack("L", len(data)) + data)

cap.release()
conn.close()
server_socket.close()

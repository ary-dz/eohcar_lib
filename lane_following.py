import cv2
import numpy as np

# Camera parameters of Raspi Cam
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def process_frame(frame):
    # Preprocessing: Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Thresholding: Detect the racing line
    _, binary = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)  # Invert for dark lines
    
    # Edge Detection: Use Canny for sharp edges
    edges = cv2.Canny(binary, 50, 150)
    
    # Line Detection: Use Hough Transform to find the racing line
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
    
    if lines is not None:
        # Average all detected lines to find a single racing line
        x_coords = []
        y_coords = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])
        
        # Fit a polynomial (linear fit since it's a straight line approximation)
        if len(x_coords) > 0 and len(y_coords) > 0:
            poly_fit = np.polyfit(y_coords, x_coords, deg=1)  # Fit line: x = m*y + b
            return poly_fit
    
    return None

def calculate_control(poly_fit):
    # Control logic based on racing line position
    if poly_fit is not None:
        m, b = poly_fit
        
        # Predict the position of the line at the bottom of the frame (y = CAMERA_HEIGHT)
        predicted_x = m * CAMERA_HEIGHT + b
        
        # Calculate error from center of the frame
        image_center_x = CAMERA_WIDTH // 2
        error = predicted_x - image_center_x
        
        # Simple proportional control for steering
        steering_gain = 0.05  # Adjust sensitivity
        steering_command = error * steering_gain
        
        return np.clip(steering_command, -1, 1)  # Normalized output (-1 for left turn, +1 for right turn)
    
    return 0  # No adjustment if no line detected

# Main processing loop
cap = cv2.VideoCapture(0)  # Use camera index (0 for default)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    poly_fit = process_frame(frame)
    steering_command = calculate_control(poly_fit)
    
    print(f"Steering Command: {steering_command:.2f}")
    
    # Display processed frame with detected line overlay (for visualization purposes)
    if poly_fit is not None:
        m, b = poly_fit
        y1, y2 = CAMERA_HEIGHT, int(CAMERA_HEIGHT * 0.6)  # Bottom and mid-frame points
        x1, x2 = int(m * y1 + b), int(m * y2 + b)
        
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=3)  # Draw detected line
    
    cv2.imshow('Racing Line Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

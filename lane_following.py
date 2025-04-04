import cv2
import numpy as np

# Camera parameters of Raspi Cam
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 640

# Perspective Transform parameters
ROI_SRC = np.float32([[20, 620],  # Bottom-left
                      [460, 620],  # Bottom-right
                      [420, 350],  # Top-right
                      [60, 350]]) # Top-left

ROI_DST = np.float32([[0, CAMERA_HEIGHT], 
                     [CAMERA_WIDTH, CAMERA_HEIGHT], 
                     [CAMERA_WIDTH, 0], 
                     [0, 0]])

# Initialize perspective transform matrix
M = cv2.getPerspectiveTransform(ROI_SRC, ROI_DST)
Minv = cv2.getPerspectiveTransform(ROI_DST, ROI_SRC)

def process_frame(frame):
    # Perspective Transform: Apply to the frame
    warped = cv2.warpPerspective(frame, M, (CAMERA_WIDTH, CAMERA_HEIGHT))
    cv2.imshow('Warped', warped)  # For debugging, show the warped image
    
    # Preprocessing: Convert to grayscale
    color = cv2.cvtColor(warped, cv2.COLOR_RGB2BGR)
    
    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(color, (5, 5), 0)
    
    mask = cv2.inRange(blur, (0, 0, 0),(150, 255, 255)) # modify your thresholds
    blur = cv2.bitwise_and(blur,blur,mask=mask)
    # cv2.imshow('color', blur)
    # Thresholding: Detect the racing line
    _, binary = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)  # Invert for dark lines
    cv2.imshow('Binary', binary)  # For debugging, show the binary image
    
    # Edge Detection: Use Canny for sharp edges
    edges = cv2.Canny(binary, 50, 150)
    cv2.imshow('Edges', edges)  # For debugging, show the edges
    
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
            poly_fit = np.polyfit(y_coords, x_coords, deg=2)  # Fit line: x = m*y + b
            return poly_fit
    
    return None

def calculate_control(poly_fit):
    # Control logic based on racing line position
    if poly_fit is not None:
        a, b, c = poly_fit  # Coefficients of the polynomial
        
        # Predict the position of the line at the bottom of the frame (y = CAMERA_HEIGHT)
        predicted_x = a * (CAMERA_HEIGHT//4)**2 + b * (CAMERA_HEIGHT//4) + c
        
        # Calculate error from center of the frame
        image_center_x = a * (CAMERA_HEIGHT)**2 + b * (CAMERA_HEIGHT) + c
        print(f"Predicted X: {predicted_x}, Image Center X: {image_center_x}")
        error = predicted_x - image_center_x
        
        # Simple proportional control for steering
        steering_gain = 0.02  # Adjust sensitivity
        # steering_command = error * steering_gain
        steering_command = error / image_center_x
        
        return np.clip(steering_command, -1, 1)  # Normalized output (-1 for left turn, +1 for right turn)
    
    return 0  # No adjustment if no line detected

def get_controls(frame):
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))  # Resize to match camera dimensions
    
    warped = cv2.warpPerspective(frame, M, (CAMERA_WIDTH, CAMERA_HEIGHT))
    
    #plot the ROI_SRC points on frame
    roi_debug_frame = frame.copy()
    for point in ROI_SRC:
        cv2.circle(roi_debug_frame, tuple(point.astype(int)), 5, (0, 255, 0), -1)
    cv2.imshow('ROI Points', roi_debug_frame)  # For debugging, show the ROI points
    
    poly_fit = process_frame(frame)
            # Display processed frame with detected line overlay (for visualization purposes)
    if poly_fit is not None:
        a, b, c = poly_fit
        y_vals = np.linspace(0, CAMERA_HEIGHT - 1, num=100).astype(int)
        x_vals = (a * y_vals**2 + b * y_vals + c).astype(int)
        
        for i in range(len(y_vals) - 1):
            cv2.line(warped,
                    (x_vals[i], y_vals[i]),
                    (x_vals[i + 1], y_vals[i + 1]),
                    color=(0, 255, 0), thickness=3)
        waypoint = a * (CAMERA_HEIGHT//4)**2 + b * (CAMERA_HEIGHT//4) + c
        cv2.circle(warped, (int(waypoint), CAMERA_HEIGHT//4), 5, (255, 0, 0), -1)
        cv2.imshow('Detected Curve', warped)  # Curve overlay
    
    steering_command = calculate_control(poly_fit)
    velocity_command = 0.3 if abs(steering_command) >= 0.2 else 1.0 # 99% sure we can get variable velocity with the controller

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
    return steering_command, velocity_command, poly_fit
# Main processing loop
# cap = cv2.VideoCapture("http://172.16.115.30:5000/camera")  # Use camera index (0 for default)
if __name__ == "__main__":
    while True:
        # ret, frame = cap.read()
        # if not ret:
        #     break
        frame = cv2.imread('/Users/georgehuber/Downloads/eoh_test_real/5.png')  # For testing, replace with actual camera capture
        steering_command, velocity_command,poly_fit = get_controls(frame)
        print(f"Steering Command: {steering_command:.2f}")
        print(f"Velocity Command: {velocity_command:.2f}")
         
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # cap.release()
    # cv2.destroyAllWindows()

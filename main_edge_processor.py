import cv2
import numpy as np
import time

# ==========================================
# CONFIGURATION SWITCH
# ==========================================
# Set to True when using Laptop Webcam
# Set to False when ESP32-CAM arrives!
USE_LAPTOP_WEBCAM = True

ESP32_CAM_STREAM_URL = "http://192.168.1.100/cam-hi.jpg"  # Update with ESP32 IP later

def get_frame(cap):
    """Abstraction layer to fetch frames seamlessly regardless of video source."""
    if USE_LAPTOP_WEBCAM:
        ret, frame = cap.read()
        return frame if ret else None
    else:
        # Fetch live JPEG buffer directly from ESP32-CAM over network
        import urllib.request
        try:
            img_resp = urllib.request.urlopen(ESP32_CAM_STREAM_URL)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            return cv2.imdecode(img_np, -1)
        except Exception as e:
            print(f"ESP32 Stream Error: {e}")
            return None

def trigger_emergency_alert(frame):
    """Simulates the emergency dispatch routing (SMS/HTTP payload)."""
    print("\n[ALERT DISPATCHED] Emergency payload sent to contacts!")
    # Save alert frame locally
    cv2.imwrite(f"alert_frame_{int(time.time())}.jpg", frame)

# ==========================================
# MAIN EXECUTION LOOP
# ==========================================
def main():
    print("Starting Bhavaani Kavach Edge Processor...")
    
    # Initialize Input Source
    cap = None
    if USE_LAPTOP_WEBCAM:
        cap = cv2.VideoCapture(0) # Open laptop webcam
        print("Connected to Laptop Webcam. Press 't' to simulate trigger, 'q' to quit.")
    
    anomaly_counter = 0

    while True:
        frame = get_frame(cap)
        if frame is None:
            continue

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Edge Processing (Canny Detection)
        edges = cv2.Canny(gray, threshold1=100, threshold2=200)

        # 3. Anomaly Analysis (Counting edge pixels)
        edge_density = np.sum(edges > 0)
        
        # Display feedback window
        cv2.putText(frame, f"Edge Density: {edge_density}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Bhavaani Kavach - Realtime Feed", frame)
        cv2.imshow("Edge Analytics", edges)

        # Keyboard Triggers (Simulating hardware button)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('t'):  # Press 't' on laptop keyboard to simulate trigger button
            print("\nManual Trigger Pressed!")
            trigger_emergency_alert(frame)
        elif key == ord('q'):
            break

    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

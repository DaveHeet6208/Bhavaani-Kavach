# week2_multi_frame_anomaly.py - Bhavaani Kavach Multi-Frame Verification
import cv2
import numpy as np
import time
import json

class BhavaaniAnomalyDetector:
    def __init__(self, motion_threshold=1500, min_burst_frames=3):
        """
        :param motion_threshold: Minimum average pixel movement score to classify an emergency.
        :param min_burst_frames: Number of consecutive frames analyzed in a single verification burst.
        """
        self.motion_threshold = motion_threshold
        self.min_burst_frames = min_burst_frames
        
        # Mock GPS Coordinates for testing (Will be replaced by Phone BLE GPS later)
        self.mock_gps = {"latitude": 22.5645, "longitude": 71.8214}

    def preprocess_frame(self, frame):
        """
        Converts frame to Grayscale and applies Gaussian Blur to filter out sensor noise.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        return blurred

    def calculate_motion_score(self, frame_burst):
        """
        Calculates absolute pixel difference across consecutive frames.
        """
        if len(frame_burst) < 2:
            return 0.0

        total_diff_pixels = 0
        processed_frames = [self.preprocess_frame(f) for f in frame_burst]

        # Calculate difference between Frame(n) and Frame(n-1)
        for i in range(len(processed_frames) - 1):
            frame_delta = cv2.absdiff(processed_frames[i], processed_frames[i + 1])
            
            # Apply binary thresholding (pixels with change > 25 are marked active)
            _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
            
            # Count non-zero (changed) pixels
            non_zero_count = cv2.countNonZero(thresh)
            total_diff_pixels += non_zero_count

        # Average motion score across frame gaps
        avg_motion_score = total_diff_pixels / (len(processed_frames) - 1)
        return avg_motion_score

    def generate_emergency_payload(self, trigger_frame, score):
        """
        Generates structured JSON metadata for downstream dispatch.
        """
        # Compress trigger image to JPEG byte stream
        success, buffer = cv2.imencode('.jpg', trigger_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        payload_size_kb = len(buffer) / 1024.0 if success else 0.0

        payload = {
            "device_id": "BHAVAANI_KAVACH_001",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "anomaly_verified": True,
            "motion_score": round(score, 2),
            "location": self.mock_gps,
            "image_payload_kb": round(payload_size_kb, 2),
            "status": "CRITICAL_ALERT_DISPATCH_REQUIRED"
        }
        return payload


def main():
    detector = BhavaaniAnomalyDetector(motion_threshold=1500, min_burst_frames=3)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open laptop webcam.")
        return

    print("\n========================================================")
    print("   BHAVAANI KAVACH - WEEK 2 MULTI-FRAME ANOMALY SUITE   ")
    print("========================================================")
    print(" Instructions:")
    print("   • Press 'SPACE' -> Captures a 3-frame burst & computes motion score")
    print("   • Press 'q'     -> Quit simulation")
    print("========================================================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Bhavaani Kavach - Live View", frame)
        key = cv2.waitKey(1) & 0xFF

        # SPACEBAR Pressed -> Run Multi-Frame Anomaly Burst
        if key == ord(' '):
            print("\n[TRIGGER ACTIVATED] Capturing 3-frame burst sequence...")
            frame_burst = [frame]

            # Rapidly capture 2 additional frames with 100ms interval
            for i in range(2):
                time.sleep(0.1)
                ret_burst, next_frame = cap.read()
                if ret_burst:
                    frame_burst.append(next_frame)

            # Calculate Motion Score
            motion_score = detector.calculate_motion_score(frame_burst)
            print(f" -> Computed Multi-Frame Motion Score: {motion_score:.2f}")

            # Verification Check
            if motion_score >= detector.motion_threshold:
                print(" -> [VERIFICATION SUCCESS] Threat/Anomaly validated!")
                payload = detector.generate_emergency_payload(frame_burst[-1], motion_score)
                print("\n" + "="*50)
                print("DISPATCH PAYLOAD GENERATED:")
                print(json.dumps(payload, indent=4))
                print("="*50 + "\n")
            else:
                print(" -> [VERIFICATION REJECTED] Motion score below safety threshold (False Alarm).")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

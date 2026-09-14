# bhavaani_core_engine.py - Integrated Core Engine
import cv2
import numpy as np
import time
import json
import winsound

class BhavaaniKavachEngine:
    def __init__(self, motion_threshold=1500, min_burst_frames=3):
        self.motion_threshold = motion_threshold
        self.min_burst_frames = min_burst_frames
        self.device_id = "BHAVAANI_KAVACH_001"
        self.mock_gps = {"latitude": 22.5645, "longitude": 71.8214}

    def preprocess_edge_map(self, frame):
        """Week 1: Preprocess frame into Canny Edge representation."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 100, 200)
        return edges

    def evaluate_burst_motion(self, frame_burst):
        """Week 2: Calculate multi-frame motion differential score."""
        if len(frame_burst) < 2:
            return 0.0

        total_diff_pixels = 0
        processed = [cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (21, 21), 0) for f in frame_burst]

        for i in range(len(processed) - 1):
            delta = cv2.absdiff(processed[i], processed[i + 1])
            _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
            total_diff_pixels += cv2.countNonZero(thresh)

        return total_diff_pixels / (len(processed) - 1)

    def trigger_audio_siren(self):
        """Week 3: Fire high-decibel local deterrent alarm."""
        print(" -> [SIREN ACTIVATED] Sounding audio alarm...")
        for _ in range(3):
            winsound.Beep(2500, 250)
            time.sleep(0.05)

    def generate_dispatch_payload(self, trigger_frame, score):
        """Week 3: Format payload & Google Maps URL."""
        success, buffer = cv2.imencode('.jpg', trigger_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        kb_size = len(buffer) / 1024.0 if success else 0.0
        maps_url = f"https://www.google.com/maps?q={self.mock_gps['latitude']},{self.mock_gps['longitude']}"

        return {
            "device_id": self.device_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "anomaly_verified": True,
            "motion_score": round(score, 2),
            "location_link": maps_url,
            "image_payload_kb": round(kb_size, 2),
            "status": "CRITICAL_ALERT_DISPATCH_REQUIRED"
        }

def main():
    engine = BhavaaniKavachEngine()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access camera.")
        return

    print("\n========================================================")
    print("      BHAVAANI KAVACH - WEEK 4 CORE ENGINE INTEGRATED   ")
    print("========================================================")
    print(" Controls:")
    print("   • Press 'SPACE' -> Capture burst & run full verification")
    print("   • Press 'q'     -> Quit system")
    print("========================================================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Dual Display Feed: Color Preview & Edge Analytics
        edge_map = engine.preprocess_edge_map(frame)
        cv2.imshow("Bhavaani Kavach - Live Color Feed", frame)
        cv2.imshow("Bhavaani Kavach - Internal Edge Map", edge_map)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            print("\n[TRIGGER DETECTED] Executing Multi-Frame Verification Burst...")
            burst_sequence = [frame]

            for _ in range(2):
                time.sleep(0.1)
                ret_b, b_frame = cap.read()
                if ret_b:
                    burst_sequence.append(b_frame)

            score = engine.evaluate_burst_motion(burst_sequence)
            print(f" -> Computed Multi-Frame Motion Score: {score:.2f}")

            if score >= engine.motion_threshold:
                print(" -> [VERIFICATION SUCCESS] Threat Confirmed!")
                engine.trigger_audio_siren()
                payload = engine.generate_dispatch_payload(burst_sequence[-1], score)
                print("\n" + "="*55)
                print("DISPATCH PAYLOAD READY FOR APP HANDOFF:")
                print(json.dumps(payload, indent=4))
                print("="*55 + "\n")
            else:
                print(" -> [VERIFICATION REJECTED] False alarm / Motion below threshold.")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

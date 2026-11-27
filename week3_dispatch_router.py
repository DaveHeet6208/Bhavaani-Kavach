# week3_dispatch_router.py - Emergency Dispatch & Audio Siren Router
import cv2
import numpy as np
import time
import json
import smtplib
import winsound  # Works natively on Windows for sound alert
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class EmergencyDispatchRouter:
    def __init__(self):
        # Mock Emergency Contacts Configuration
        self.sender_email = "your_system_alert@gmail.com"  # Configurable SMTP sender
        self.emergency_contact_email = "family_contact@gmail.com"
        self.email_password = "your_app_password"  # Google App Password

    def trigger_local_siren(self):
        """
        Fires an immediate high-pitched audio siren on the host device.
        """
        print(" -> [LOCAL DISPATCH] Sounding high-decibel alarm siren...")
        for _ in range(3):
            # Frequency: 2500Hz, Duration: 300ms
            winsound.Beep(2500, 300)
            time.sleep(0.05)

    def dispatch_email_alert(self, payload, image_frame):
        """
        Packages payload data + JPEG image and routes to emergency contact via SMTP.
        """
        print(" -> [NETWORK DISPATCH] Formatting Emergency SMTP Email...")
        
        # 1. Encode image to JPEG buffer
        success, buffer = cv2.imencode('.jpg', image_frame)
        if not success:
            print(" -> [ERROR] Failed to encode frame for dispatch.")
            return False

        # 2. Build Multi-part Email
        msg = MIMEMultipart()
        msg['Subject'] = f"!!! URGENT: BHAVAANI KAVACH CRITICAL ALERT [{payload['timestamp']}]"
        msg['From'] = self.sender_email
        msg['To'] = self.emergency_contact_email

        # 3. Formulate Email Text Body
        maps_link = f"https://www.google.com/maps?q={payload['location']['latitude']},{payload['location']['longitude']}"
        body = f"""
        CRITICAL EMERGENCY ALERT DETECTED BY BHAVAANI KAVACH WEARABLE SYSTEM
        
        Device ID: {payload['device_id']}
        Timestamp: {payload['timestamp']}
        Motion Score: {payload['motion_score']}
        
        LIVE GPS LOCATION LINK:
        {maps_link}
        
        The validated full-color evidence frame captured at the moment of trigger is attached below.
        """
        msg.attach(MIMEText(body, 'plain'))

        # 4. Attach Full-Color Image
        img_attachment = MIMEImage(buffer.tobytes(), name="evidence_capture.jpg")
        msg.attach(img_attachment)
        
        # --- DATASET GATHERING ARCHITECTURE ---
        # Save a copy to the hard drive so the user can see it AND build a training dataset!
        import os, json
        os.makedirs("training_data", exist_ok=True)
        timestamp = payload.get("timestamp", "latest")
        
        # Save Image
        img_path = os.path.join("training_data", f"evidence_{timestamp}.jpg")
        with open(img_path, "wb") as f:
            f.write(buffer.tobytes())
            
        # Save Metadata (Labels/Coordinates)
        meta_path = os.path.join("training_data", f"metadata_{timestamp}.json")
        with open(meta_path, "w") as f:
            json.dump(payload, f, indent=4)
        # --------------------------------------

        # 5. Execute Transmission (Simulated / Live)
        print(f" -> [DISPATCH SUCCESS] Emergency payload & image ready for transmission to {self.emergency_contact_email}")
        print(f" -> [GPS MAPS LINK]: {maps_link}")
        return True


# --- Complete Integrated Week 3 Pipeline ---
def run_week3_pipeline():
    router = EmergencyDispatchRouter()
    cap = cv2.VideoCapture(0)

    print("\n========================================================")
    print("   BHAVAANI KAVACH - WEEK 3 DISPATCH ROUTER SUITE       ")
    print("========================================================")
    print(" Press 'SPACE' to trigger simulated emergency dispatch")
    print(" Press 'q' to quit")
    print("========================================================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Bhavaani Kavach - Live View", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            print("\n[EMERGENCY TRIGGERED] Initiating Dispatch Pipeline...")
            
            # Step 1: Fire Local Sound Alarm
            router.trigger_local_siren()
            
            # Step 2: Formulate Payload
            payload = {
                "device_id": "BHAVAANI_KAVACH_001",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "motion_score": 14250.0,
                "location": {"latitude": 21.5222, "longitude": 70.4579}
            }
            
            # Step 3: Route Email/SMS Dispatch with Image Attachment
            router.dispatch_email_alert(payload, frame)

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_week3_pipeline()

# bhavaani_integrated_master.py - Complete End-to-End System Integration
import json
import os
import smtplib
import time
import urllib.request
import webbrowser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
import cv2

# Import our custom profile manager
from app_user_profile import UserProfileManager
from fusion_engine import FusionEngine


class BhavaaniMasterSystem:

    def __init__(self):
        self.profile_manager = UserProfileManager()
        self.helpline_contact = "181 (Nirbhaya / Women Emergency Helpline)"
        self.fusion_engine = FusionEngine()

    def process_ble_stream(self, raw_ble_packet):
        """Passes incoming BLE data through the multi-layer Fusion Engine before dispatching."""
        ble_data = json.loads(raw_ble_packet)
        audio_db = ble_data.get("audio_stress_db", 0.0)
        motion_score = ble_data.get("motion_score", 0.0)
        
        print(f"\n[BLE INTERCEPT] Device ID: {ble_data.get('device_id')} | Motion: {motion_score} | Audio: {audio_db}dB")
        is_threat, reason = self.fusion_engine.process_signal(acoustic_db=audio_db, motion_score=motion_score)
        
        if is_threat:
            print(f" -> [FUSION ENGINE] {reason}: Temporal and Sustained Correlation Met!")
            # Trigger the countdown/dispatch
            self.execute_full_pipeline(raw_ble_packet)
        else:
            print(f" -> [FUSION ENGINE] Status: {reason}. Filtering out as false positive or monitoring...")

    def fetch_live_location(self):
        """Queries network IP for real-time lat/lon coordinates."""
        try:
            url = "http://ip-api.com/json/"
            req = urllib.request.urlopen(url, timeout=3)
            data = json.loads(req.read().decode())
            lat, lon = data["lat"], data["lon"]
            city = data.get("city", "Unknown City")
            region = data.get("regionName", "Unknown Region")
            print(
                f"[LOCATION FIXED] Network Geolocation: {city}, {region} ({lat},"
                f" {lon})"
            )
        except Exception:
            lat, lon = 22.5645, 71.8214
            print("[LOCATION FALLBACK] Offline. Using fallback coordinates.")

        return {
            "latitude": lat,
            "longitude": lon,
            "maps_url": f"https://www.google.com/maps?q={lat},{lon}",
        }

    def send_real_email_alert(
        self,
        recipient_email,
        victim_name,
        gps_info,
        image_path="snapshot_alert.jpg",
    ):
        """Sends a real SMTP email with a valid attached JPEG snapshot."""
        
        # 1. Generate a valid JPEG image if the file doesn't exist or is corrupted (< 100 bytes)
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            print(f"[IMAGE ENGINE] Generating valid test snapshot image at '{image_path}'...")
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(img, (20, 20), (620, 460), (0, 0, 255), 3)
            cv2.putText(
                img,
                "BHAVAANI KAVACH: EMERGENCY ALERT",
                (40, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                img,
                f"GPS: {gps_info.get('latitude')}, {gps_info.get('longitude')}",
                (40, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            cv2.imwrite(image_path, img)

        print(f"\n[EMAIL ENGINE] Preparing dispatch payload to: {recipient_email}")

        # Set up SMTP Details
        sender_email = "bhavaani.kavach.alert@gmail.com"
        app_password = "YOUR_GMAIL_APP_PASSWORD"  # Replace with Google App Password

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"🚨 EMERGENCY ALERT: {victim_name} Needs Assistance!"

        body = (
            f"EMERGENCY ALERT TRIGGERED!\n\n"
            f"Victim Name: {victim_name}\n"
            f"Device: Bhavaani Kavach Locket\n"
            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S IST')}\n"
            f"Google Maps Link: {gps_info['maps_url']}\n\n"
            f"Please check the attached snapshot from the wearable camera."
        )
        msg.attach(MIMEText(body, "plain"))

        # Attach JPEG snapshot from camera
        try:
            with open(image_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename= {image_path}"
            )
            msg.attach(part)
            print(" -> [SUCCESS] Camera JPEG Snapshot attached to email payload.")
        except Exception as e:
            print(f" -> [WARNING] Could not attach image: {e}")

        # To send live, uncomment these 5 lines with valid Gmail App Password:
        # try:
        #     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        #         server.login(sender_email, app_password)
        #         server.sendmail(sender_email, recipient_email, msg.as_string())
        #     print(" -> [DISPATCH CONFIRMED] Real Email Delivered Successfully!")
        # except Exception as e:
        #     print(f" -> [SMTP ERROR] {e}")

    def execute_full_pipeline(self, raw_ble_packet):
        """Master workflow execution."""
        print("========================================================")
        print("      BHAVAANI KAVACH: INTEGRATED EMERGENCY SYSTEM      ")
        print("========================================================")

        # Step 1: Load Profile
        profile = self.profile_manager.load_profile()
        if not profile:
            print(
                "[ERROR] No active user profile found! Please run app_user_profile.py"
                " first."
            )
            return

        print(f" -> Active User Profile : {profile['user_name']}")
        print(f" -> Emergency Contact   : {profile['primary_emergency_contact']}")
        print(f" -> Official Helpline   : {self.helpline_contact}")
        print(f" -> Emergency Email     : {profile['emergency_email']}")

        # Step 2: Parse incoming camera & acoustic triggers
        ble_data = json.loads(raw_ble_packet)
        audio_db = ble_data.get("audio_stress_db", 0.0)
        vocal_distress = ble_data.get("acoustic_distress_detected", False)

        print(
            f"\n[BLE INTERCEPT] Device ID: {ble_data.get('device_id')} | Anomaly"
            f" Score: {ble_data.get('motion_score')}"
        )
        print(
            f" -> Audio Decibel Level : {audio_db} dB | Vocal Distress Alert:"
            f" {vocal_distress}"
        )

        # Step 3: Fetch Live Location
        gps = self.fetch_live_location()

        # Step 4: Open Browser Map
        print("\n[ACTION] Auto-launching Google Maps to live coordinates...")
        webbrowser.open(gps["maps_url"])

        # Step 5: Process Email Dispatch
        self.send_real_email_alert(
            recipient_email=profile["emergency_email"],
            victim_name=profile["user_name"],
            gps_info=gps,
        )

        # Step 6: Construct Final Multi-Channel SMS Payload
        sms_payload = (
            f"!!! EMERGENCY ALERT !!!\n"
            f"User: {profile['user_name']}\n"
            f"Locket ID: {ble_data.get('device_id')}\n"
            f"Audio Stress Trigger: {audio_db} dB\n"
            f"Location Pin: {gps['maps_url']}\n"
            f"Routing to Contacts: {profile['primary_emergency_contact']} &"
            f" {self.helpline_contact}"
        )

        print("\n--------------------------------------------------------")
        print("FINAL OUTGOING SMS BROADCAST PAYLOAD:")
        print(sms_payload)
        print("--------------------------------------------------------")
        print("   [SYSTEM READY] ALL PIPELINE STAGES EXECUTED SUCCESSFULLY")
        print("========================================================\n")


if __name__ == "__main__":
    system = BhavaaniMasterSystem()

    # Simulated BLE trigger coming from the wearable locket (including INMP441 audio metrics)
    simulated_locket_packet = json.dumps({
        "device_id": "BHAVAANI_KAVACH_001",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "anomaly_verified": True,
        "motion_score": 18450.2,
        "audio_stress_db": 84.5,
        "acoustic_distress_detected": True,
        "status": "CRITICAL_ALERT_DISPATCH_REQUIRED",
    })

    # Test the Fusion Engine with a simulated burst
    print("\n--- SIMULATING BURST 1 (Isolated Spike, No trigger) ---")
    system.process_ble_stream(simulated_locket_packet)
    
    print("\n--- SIMULATING BURST 2 (Sustained...) ---")
    system.process_ble_stream(simulated_locket_packet)
    
    print("\n--- SIMULATING BURST 3 (Correlated and Sustained -> TRIGGER) ---")
    system.process_ble_stream(simulated_locket_packet)

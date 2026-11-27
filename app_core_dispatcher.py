# app_core_dispatcher.py - Integrated Mobile App Dispatcher
import json
import time
import os
from app_user_profile import UserProfileManager

class BhavaaniMobileAppEngine:
    def __init__(self):
        self.profile_manager = UserProfileManager()

    def get_smartphone_gps(self):
        """Simulates reading current phone GPS coordinates."""
        lat, lon = 22.5645, 71.8214
        return {
            "latitude": lat,
            "longitude": lon,
            "maps_url": f"https://www.google.com/maps?q={lat},{lon}"
        }

    def process_incoming_ble_packet(self, raw_json_payload):
        """Processes incoming BLE payload and routes alerts using saved profile data."""
        # Step 1: Load active user profile from JSON storage
        profile = self.profile_manager.load_profile()
        
        if not profile:
            print("\n[CRITICAL ERROR] No active user profile found! Run app_user_profile.py first.")
            return None

        # Step 2: Parse incoming BLE camera data
        data = json.loads(raw_json_payload)
        gps = self.get_smartphone_gps()

        # Step 3: Construct personalized emergency message
        sms_text = (
            f"!!! EMERGENCY ALERT !!!\n"
            f"User: {profile['user_name']}\n"
            f"Bhavaani Kavach Locket Triggered!\n"
            f"Motion Anomaly Score: {data.get('motion_score')}\n"
            f"Time: {data.get('timestamp')}\n"
            f"Live Location: {gps['maps_url']}\n"
            f"Immediate assistance required!"
        )

        print("\n========================================================")
        print("    MOBILE APP: EMERGENCY DISPATCH PIPELINE EXECUTED    ")
        print("========================================================")
        print(f" -> User Name       : {profile['user_name']}")
        print(f" -> Recipient Phone : {profile['primary_emergency_contact']}")
        print(f" -> Recipient Email : {profile['emergency_email']}")
        print("--------------------------------------------------------")
        print(" OUTGOING EMERGENCY SMS PAYLOAD:")
        print(sms_text)
        print("--------------------------------------------------------")

        return {
            "status": "DISPATCH_SUCCESSFUL",
            "sent_to_contact": profile['primary_emergency_contact'],
            "sent_to_email": profile['emergency_email'],
            "maps_link": gps['maps_url'],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S IST", time.localtime())
        }

if __name__ == "__main__":
    dispatcher = BhavaaniMobileAppEngine()
    
    # Mock BLE packet forwarded from Week 4 Core Engine
    mock_ble_data = json.dumps({
        "device_id": "BHAVAANI_KAVACH_001",
        "timestamp": "2026-08-23 11:59:01 UTC",
        "anomaly_verified": True,
        "motion_score": 16131.5,
        "status": "CRITICAL_ALERT_DISPATCH_REQUIRED"
    })
    
    receipt = dispatcher.process_incoming_ble_packet(mock_ble_data)
    
    if receipt:
        print("\nFINAL DISPATCH RECEIPT:")
        print(json.dumps(receipt, indent=4))

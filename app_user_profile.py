# app_user_profile.py - Secure Profile & Local Storage Module
import json
import os
import re

PROFILE_FILE = "user_profile.json"

class UserProfileManager:
    def __init__(self, storage_path=PROFILE_FILE):
        self.storage_path = storage_path

    def validate_phone(self, phone):
        pattern = r"^\+?[1-9]\d{1,14}$"
        return bool(re.match(pattern, phone))

    def validate_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def save_profile(self, user_name, primary_contact, emergency_email, user_address=""):
        if not self.validate_phone(primary_contact):
            raise ValueError("Invalid phone number! Use E.164 format (e.g., +919876543210).")
            
        if not self.validate_email(emergency_email):
            raise ValueError("Invalid email format! Example: contact@domain.com")

        profile_data = {
            "user_name": user_name,
            "primary_emergency_contact": primary_contact,
            "emergency_email": emergency_email,
            "home_address": user_address,
            "setup_completed": True
        }

        with open(self.storage_path, "w") as f:
            json.dump(profile_data, f, indent=4)
            
        print("\n[SUCCESS] User Profile Saved Successfully!")
        return profile_data

    def load_profile(self):
        if not os.path.exists(self.storage_path):
            return None

        with open(self.storage_path, "r") as f:
            return json.load(f)

    def delete_profile_safely(self):
        """Requests explicit user permission before deleting stored profile data."""
        if not os.path.exists(self.storage_path):
            print("\n[INFO] No profile exists to erase.")
            return False

        profile = self.load_profile()
        print("\n========================================================")
        print("                ATTENTION: ERASE DATA                   ")
        print("========================================================")
        print(f" Target User Profile: {profile.get('user_name')}")
        print(f" Saved Contact      : {profile.get('primary_emergency_contact')}")
        print("--------------------------------------------------------")
        
        # Explicit Permission Check
        consent = input("Are you sure you want to permanently erase these details? (y/n): ").strip().lower()
        
        if consent == 'y':
            os.remove(self.storage_path)
            print("\n[CONFIRMED] Profile erased successfully. Storage is clean.")
            return True
        else:
            print("\n[CANCELLED] Erasure aborted. Your details remain completely safe!")
            return False


def main():
    manager = UserProfileManager()
    
    while True:
        profile = manager.load_profile()
        print("\n========================================================")
        print("        BHAVAANI KAVACH - PROFILE MANAGER MENU          ")
        print("========================================================")
        
        if profile:
            print(f" Active Profile: {profile['user_name']}")
            print(f" Saved Phone   : {profile['primary_emergency_contact']}")
            print(f" Saved Email   : {profile['emergency_email']}")
            print("--------------------------------------------------------")
            print(" Options: [1] Update Details  [2] Erase Profile  [3] Exit Menu")
        else:
            print(" [STATUS] No active user profile configured.")
            print("--------------------------------------------------------")
            print(" Options: [1] Create New Profile  [3] Exit Menu")

        choice = input("\nSelect Option (1/2/3): ").strip()

        if choice == '1':
            print("\n--- ENTER EMERGENCY DETAILS ---")
            name = input("Enter Full Name: ").strip()
            contact = input("Enter Emergency Phone (e.g., +919876543210): ").strip()
            email = input("Enter Emergency Email: ").strip()
            
            try:
                manager.save_profile(name, contact, email)
            except ValueError as e:
                print(f"\n[ERROR] {e}")

        elif choice == '2' and profile:
            manager.delete_profile_safely()

        elif choice == '3':
            print("\nExiting Profile Manager. Data synced.")
            break
        else:
            print("\n[INVALID OPTION] Please select a valid menu choice.")

if __name__ == "__main__":
    main()

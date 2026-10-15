import flet as ft
import time
import threading
import json
import os
import cv2
import numpy as np
import random
import sounddevice as sd
import vosk
import json
import collections
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
# Import backend modules
from app_user_profile import UserProfileManager
from week3_dispatch_router import EmergencyDispatchRouter
from bhavaani_integrated_master import BhavaaniMasterSystem
from fusion_engine import FusionEngine

# Global flag to prevent multiple threads from fighting over the webcam
hardware_thread_running = False

def main(page: ft.Page):
    page.title = "Bhavaani Kavach - AI Security Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # Mobile app format
    page.window.width = 420
    page.window.height = 900
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap",
    }
    
    # Minimalist Theme Setup
    page.theme = ft.Theme(
        font_family="Inter", 
        color_scheme_seed=ft.Colors.INDIGO,
    )
    # App Bar Removed for a cleaner iOS-style header inside the dashboard

    # Backend Instances
    profile_manager = UserProfileManager()
    dispatch_router = EmergencyDispatchRouter()
    fusion_engine = FusionEngine()
    
    # State Variables
    current_profile = profile_manager.load_profile() or {}
    
    # ----------------------------------------------------
    # DASHBOARD TAB
    # ----------------------------------------------------
    
    def create_widget_card(text, color, icon):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=28, color=color),
                ft.Container(height=4),
                ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=110,
            height=110,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        )
        
    badges_row = ft.Row([
        create_widget_card("BLE TETHER", ft.Colors.BLUE_400, ft.Icons.BLUETOOTH_CONNECTED),
        create_widget_card("ACOUSTIC AI", ft.Colors.PURPLE_400, ft.Icons.RECORD_VOICE_OVER),
        create_widget_card("FIFO CACHE", ft.Colors.TEAL_400, ft.Icons.STORAGE),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10)
    
    # Minimalist Apple-HomeKit Style Video Feed
    video_feed = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.VIDEOCAM, size=32, color=ft.Colors.WHITE_38),
            ft.Container(height=5),
            ft.Text("CAMERA IN STANDBY", size=13, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE_54),
            ft.Text("Local AI Processing", size=11, color=ft.Colors.TEAL_400, weight=ft.FontWeight.W_500)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=float('inf'),
        height=220,
        border_radius=24,
        bgcolor=ft.Colors.GREY_900,
        border=ft.Border.all(1, ft.Colors.WHITE_12),
        alignment=ft.Alignment(0, 0),
    )
    
    # ----------------------------------------------------
    # AI EXECUTION & ALARM LOGIC
    # ----------------------------------------------------
    alarm_timer = None
    countdown_text = ft.Text("10", size=72, weight=ft.FontWeight.W_900, color=ft.Colors.RED_ACCENT)
    pin_input = ft.TextField(
        label="Enter PIN to Disarm", 
        password=True, 
        can_reveal_password=True,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        border_color=ft.Colors.WHITE_24,
        focused_border_color=ft.Colors.RED_400
    )
    
    def execute_sos(is_duress=False, is_tamper=False, captured_frame=None, acoustic_db=0.0, motion_score=0.0):
        """Executes the AI workflow and Dispatcher from the Pitch"""
        
        # 1. Edge License Plate Recognition (LPR) Simulation
        plates = ["DL 8C NB 1234", "MH 02 AB 9988", "GJ 01 XX 7766"]
        extracted_plate = random.choice(plates) if not is_tamper else "UNKNOWN (Locket Detached)"
        
        if not is_tamper:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"OpenCV LPR Executed: Extracted Plate [{extracted_plate}] in 420ms", color=ft.Colors.WHITE), 
                bgcolor=ft.Colors.PURPLE_800
            )
            page.snack_bar.open = True
            page.update()
            time.sleep(1.5) # Simulate processing delay
            
        # 2. Formulate Payload (Including LKP Anchor logic)
        if captured_frame is not None:
            frame = captured_frame
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
        event_type = "BLE TAMPER (LKP ANCHOR)" if is_tamper else ("DURESS ALARM" if is_duress else "ACOUSTIC STRESS ALARM")
        cv2.putText(frame, event_type, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        payload = {
            "device_id": "BHAVAANI_KAVACH_001",
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "acoustic_db": round(acoustic_db, 2),
            "motion_score": motion_score,
            "license_plate": extracted_plate,
            "location": {"latitude": 22.5645, "longitude": 71.8214}, # This would be the Last Known Point (LKP)
            "status": "TAMPER_LKP_ANCHOR" if is_tamper else "ACTIVE_CRISIS"
        }
        
        # 3. Fire dual-channel webhook (ERSS-112 and Family)
        page.snack_bar = ft.SnackBar(content=ft.Text("Pushing Dual-Channel Webhook (ERSS-112 + Family) & Uploading to AWS S3..."), bgcolor=ft.Colors.RED_900)
        page.snack_bar.open = True
        page.update()
        
        dispatch_router.trigger_local_siren()
        dispatch_router.dispatch_email_alert(payload, frame)

    def close_alarm_modal():
        page.dialog.open = False
        pin_input.value = ""
        pin_input.error_text = None
        page.update()

    def on_pin_submit(e):
        nonlocal alarm_timer
        entered_pin = pin_input.value.strip()
        expected_pin = current_profile.get("cancel_pin", "1234")
        
        if entered_pin == expected_pin:
            alarm_timer = -1 
            close_alarm_modal()
            page.snack_bar = ft.SnackBar(content=ft.Text("Alarm Disarmed.", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_800)
            page.snack_bar.open = True
            page.update()
        elif entered_pin == "9999":
            alarm_timer = -1
            close_alarm_modal()
            page.snack_bar = ft.SnackBar(content=ft.Text("System Reset.", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREY_900)
            page.snack_bar.open = True
            page.update()
            threading.Thread(target=execute_sos, args=(True, False), daemon=True).start()
        else:
            pin_input.error_text = "Invalid PIN"
            page.update()

    pin_btn = ft.FilledButton("DISARM", on_click=on_pin_submit, width=200, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE))
    
    alarm_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("ACOUSTIC DISTRESS DETECTED", color=ft.Colors.RED_ACCENT, weight=ft.FontWeight.W_800, text_align=ft.TextAlign.CENTER, size=16),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Dispatching SOS in:", text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE_70),
                countdown_text,
                ft.Container(height=10),
                pin_input,
                ft.Container(height=10),
                pin_btn
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            width=320, padding=20,
        ),
        bgcolor=ft.Colors.GREY_900,
        shape=ft.RoundedRectangleBorder(radius=16)
    )
    
    def countdown_thread(live_frame=None, acoustic_db=0.0, motion_score=0.0):
        nonlocal alarm_timer
        alarm_timer = 10
        while alarm_timer > 0:
            countdown_text.value = str(alarm_timer)
            page.update()
            time.sleep(1)
            alarm_timer -= 1
            if alarm_timer == -1: return # Interrupted by valid PIN or Safe Word
        
        if alarm_timer == 0:
            close_alarm_modal()
            execute_sos(captured_frame=live_frame, acoustic_db=acoustic_db, motion_score=motion_score)

    def trigger_acoustic_sim(e):
        """Simulates the Locket mic picking up distress audio."""
        page.dialog = alarm_modal
        alarm_modal.open = True
        page.update()
        threading.Thread(target=countdown_thread, daemon=True).start()

    def trigger_tamper_drop_sim(e):
        """Simulates the Anti-Tamper Anchor Protocol (BLE Flatline)."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text("CRITICAL: BLE FLATLINE! Locket Ripped Off. Anchoring LKP!", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_900,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()
        # No countdown. Immediate dispatch.
        threading.Thread(target=execute_sos, args=(False, True), daemon=True).start()

    def voice_safe_word_sim(e):
        """Simulates the 'Safe Return Auto-Purge' via voice command."""
        nonlocal alarm_timer
        if alarm_timer is not None and alarm_timer > 0:
            alarm_timer = -1 # Stop countdown
            close_alarm_modal()
            
        # --- CACHE SWEEP FOR PRIVACY ---
        if os.path.exists("training_data"):
            import glob
            for f in glob.glob("training_data/*"):
                try:
                    os.remove(f)
                except Exception as ex:
                    print(f"Failed to purge {f}: {ex}")
            print("\n[PRIVACY] Completed full cache sweep of all transient video/image evidence.")
            
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🎙️ Command: 'Bhavaani, Stand down'.\nPurged Video/Image Cache. Privacy Maintained.", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_800,
            duration=4000
        )
        page.snack_bar.open = True
        page.update()

    # Modern Solid Action Button
    sos_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.WHITE, size=24),
            ft.Text("MANUAL SOS", size=16, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        bgcolor=ft.Colors.RED_600,
        border_radius=ft.BorderRadius.all(16),
        alignment=ft.Alignment(0, 0),
        height=65,
        ink=True,
        on_click=lambda e: threading.Thread(target=execute_sos, daemon=True).start()
    )
    
    def trigger_fusion_engine_sim(e):
        """Simulates 3 consecutive bursts of correlated motion and audio to pass the Fusion Engine!"""
        page.snack_bar = ft.SnackBar(content=ft.Text("Feeding sensor data into Fusion Engine..."), bgcolor=ft.Colors.BLUE_GREY_800, duration=1000)
        page.snack_bar.open = True
        page.update()
        
        def run_fusion_sim():
            for i in range(1, 4):
                time.sleep(1.2)
                # Feed high acoustic (85dB) and high motion (2000)
                is_threat, reason = fusion_engine.process_signal(acoustic_db=85.0, motion_score=2000.0)
                if is_threat:
                    # Layer 4 Confirmed! Trigger the actual UI Alarm!
                    page.dialog = alarm_modal
                    alarm_modal.open = True
                    page.update()
                    threading.Thread(target=countdown_thread, daemon=True).start()
                else:
                    # Just show processing status
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Fusion Engine Burst {i}/3: {reason}"), bgcolor=ft.Colors.ORANGE_800, duration=1000)
                    page.snack_bar.open = True
                    page.update()
                    
        threading.Thread(target=run_fusion_sim, daemon=True).start()

    sim_btn_style = ft.ButtonStyle(
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=12),
        padding=16
    )
    
    sim_col = ft.Column([
        ft.Text("Developer Tools", size=14, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE_54),
        ft.FilledButton("🚀 Threat Burst Simulation", on_click=trigger_fusion_engine_sim, style=sim_btn_style, width=float('inf')),
        ft.FilledButton("🎙️ Acoustic Distress Override", on_click=trigger_acoustic_sim, style=sim_btn_style, width=float('inf')),
        ft.FilledButton("🔗 BLE Tamper Flatline", on_click=trigger_tamper_drop_sim, style=sim_btn_style, width=float('inf')),
        ft.FilledButton("✅ Safe-Word Purge", on_click=voice_safe_word_sim, style=sim_btn_style, width=float('inf'))
    ], spacing=10)
    
    dashboard_view = ft.Container(
        content=ft.Column([
            ft.Container(height=30), # Top padding replacement for AppBar
            ft.Text("Overview", size=32, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
            ft.Container(height=10),
            badges_row,
            ft.Container(height=20),
            video_feed,
            ft.Container(height=20),
            sos_btn,
            ft.Container(height=30),
            sim_col,
            ft.Container(height=40),
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.START, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=25,
        expand=True
    )
    
    # ----------------------------------------------------
    # PROFILE EDITOR TAB
    # ----------------------------------------------------
    
    def create_textfield(label, value, icon, password=False):
        return ft.TextField(
            label=label,
            value=value,
            prefix_icon=icon,
            password=password,
            can_reveal_password=password,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.INDIGO_ACCENT,
            content_padding=20
        )

    p_name = create_textfield("Full Name", current_profile.get("user_name", ""), ft.Icons.PERSON)
    p_phone = create_textfield("Family Network (WhatsApp/SMS)", current_profile.get("primary_emergency_contact", ""), ft.Icons.PHONE)
    p_email = create_textfield("ERSS-112 Webhook Email", current_profile.get("emergency_email", ""), ft.Icons.EMAIL)
    p_pin = create_textfield("Disarm PIN", current_profile.get("cancel_pin", "1234"), ft.Icons.PASSWORD, password=True)
    
    def save_profile_ui(e):
        try:
            profile_manager.save_profile(p_name.value, p_phone.value, p_email.value)
            profile_data = profile_manager.load_profile()
            profile_data["cancel_pin"] = p_pin.value
            
            with open(profile_manager.storage_path, "w") as f:
                json.dump(profile_data, f, indent=4)
                
            nonlocal current_profile
            current_profile = profile_data
            
            page.snack_bar = ft.SnackBar(ft.Text("Profile Updated Successfully", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_800)
            page.snack_bar.open = True
            page.update()
        except ValueError as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Validation Error: {err}", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED_800)
            page.snack_bar.open = True
            page.update()

    profile_view = ft.Container(
        content=ft.Column([
            ft.Text("Onboarding Configuration", size=24, weight=ft.FontWeight.W_800),
            ft.Divider(color=ft.Colors.WHITE_12, height=20),
            p_name,
            p_phone,
            p_email,
            ft.Container(height=10),
            ft.Text("Security Settings", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE_70),
            p_pin,
            ft.Text("Note: Silent Duress PIN is permanently set to 9999", size=12, color=ft.Colors.RED_400, italic=True),
            ft.Container(height=20),
            ft.FilledButton(
                "SAVE CONFIGURATION", 
                on_click=save_profile_ui, 
                width=float('inf'), 
                height=55,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_600, 
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=12)
                )
            )
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        padding=25,
        expand=True
    )

    # ----------------------------------------------------
    # MAIN LAYOUT & HARDWARE FALLBACK THREAD
    # ----------------------------------------------------
    
    main_content = ft.Container(content=dashboard_view, expand=True)

    def on_nav_change(e):
        main_content.content = dashboard_view if e.control.selected_index == 0 else profile_view
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Profile"),
        ],
        on_change=on_nav_change,
        selected_index=0
    )
    
    page.add(main_content)
    
    def hardware_monitor_thread():
        global hardware_thread_running
        if hardware_thread_running:
            return  # Prevent duplicate threads on browser refresh
        hardware_thread_running = True
        
        print("Starting LIVE Laptop Sensor Verification Thread...")
        cap = cv2.VideoCapture(0)
        prev_frame = None
        fs = 16000
        duration = 1.0  # 1-second rolling windows
        
        # Initialize Offline Voice AI
        print("Loading Vosk Offline Voice Model...")
        if os.path.exists("model"):
            vosk_model = vosk.Model("model")
            recognizer = vosk.KaldiRecognizer(vosk_model, fs)
            print("Vosk Model Loaded Successfully!")
        else:
            recognizer = None
            print("Vosk model not found. Voice commands disabled.")
            
        # Initialize YOLO Static Weapon Detection
        print("Loading YOLOv8-Nano Weapon Detection Model...")
        if YOLO is not None:
            weapon_model = YOLO("yolov8n.pt")
            # COCO Classes: 43=knife, 34=baseball bat, 76=scissors
            WEAPON_CLASSES = [43, 34, 76]
            print("YOLO Weapon Model Loaded Successfully!")
        else:
            weapon_model = None
            print("Ultralytics not installed. Static weapon detection disabled.")
            
        # --- FIFO ROLLING VIDEO BUFFER ---
        # Holds a sliding window of the last 40 frames in RAM (Zero hard drive space used until triggered)
        video_buffer = collections.deque(maxlen=40)
        
        while True:
            try:
                # 1. Capture 1 second of Audio
                audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
                sd.wait()
                
                # --- VOSK OFFLINE SPEECH RECOGNITION ---
                if recognizer is not None:
                    int16_audio = (audio_data * 32767).astype(np.int16).tobytes()
                    if recognizer.AcceptWaveform(int16_audio):
                        res = json.loads(recognizer.Result())
                        text = res.get("text", "")
                        if text:
                            print(f"[VOICE AI] Heard: '{text}'")
                            if "stop" in text or "stand down" in text:
                                print("\n>>> SAFE WORD DETECTED! DISARMING ALARM! <<<")
                                voice_safe_word_sim(None)
                                fusion_engine.acoustic_history.clear()
                                fusion_engine.motion_history.clear()
                                fusion_engine.sustained_burst_count = 0
                
                # Fix float32 overflow warning by casting to float64 before squaring
                rms = np.sqrt(np.mean(np.square(audio_data, dtype=np.float64)))
                acoustic_db = 20 * np.log10(rms) + 120 if rms > 0 else 0
                
                # 2. Capture Frame for Motion (Flush buffer first to avoid stale/exposure-shifted frames)
                for _ in range(5):
                    cap.grab()
                ret, frame = cap.read()
                
                motion_score = 0
                weapon_detected = False
                
                if ret:
                    # Append the raw frame to the Rolling Video Buffer (Throws away the oldest frame automatically)
                    video_buffer.append(frame.copy())
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
                    if prev_frame is not None:
                        delta = cv2.absdiff(prev_frame, blurred)
                        # Increased threshold from 25 to 40 to ignore webcam auto-exposure flicker
                        _, thresh = cv2.threshold(delta, 40, 255, cv2.THRESH_BINARY)
                        motion_score = cv2.countNonZero(thresh)
                    prev_frame = blurred
                    
                    # YOLO Static Weapon Check
                    if weapon_model is not None:
                        # Lowered confidence from 0.5 to 0.25 because the nano model is less confident on small objects like scissors
                        results = weapon_model(frame, classes=WEAPON_CLASSES, conf=0.25, verbose=False)
                        for r in results:
                            if len(r.boxes) > 0:
                                weapon_detected = True
                                print("\n>>> STATIC WEAPON DETECTED (Knife/Bat/Scissors)! <<<")
                                # Draw bounding boxes directly on the evidence frame!
                                frame = r.plot()
                                break
                
                print(f"[LIVE SENSORS] Acoustic: {acoustic_db:.1f} dB | Motion: {motion_score} | Weapon: {weapon_detected}")
                
                # 3. Feed to Fusion Engine
                is_threat, reason = fusion_engine.process_signal(
                    acoustic_db=acoustic_db, 
                    motion_score=motion_score, 
                    weapon_detected=weapon_detected
                )
                
                if is_threat:
                    print(f"!!! [LIVE THREAT VERIFIED] {reason} !!!")
                    
                    # Dump the FIFO Video Buffer to an AVI file for Evidence!
                    os.makedirs("training_data", exist_ok=True)
                    video_filename = f"training_data/incident_video_{time.strftime('%Y%m%d_%H%M%S')}.avi"
                    if len(video_buffer) > 0:
                        print(f"-> Stitching {len(video_buffer)} buffered RAM frames into PRE-ATTACK Video Evidence...")
                        height, width, _ = video_buffer[0].shape
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        # 5.0 FPS is roughly the loop speed depending on CPU
                        out = cv2.VideoWriter(video_filename, fourcc, 5.0, (width, height)) 
                        for buffered_frame in video_buffer:
                            out.write(buffered_frame)
                        out.release()
                        print(f"-> Pre-Attack Video Evidence successfully saved to: {video_filename}")
                    
                    # Pop the Flet UI modal
                    page.dialog = alarm_modal
                    alarm_modal.open = True
                    page.update()
                    threading.Thread(target=countdown_thread, args=(frame, acoustic_db, motion_score), daemon=True).start()
                    
                    time.sleep(15)  # Pause sensing while alarm is active
                    prev_frame = None
                    video_buffer.clear() # Clear the buffer after an event
                    
            except Exception as e:
                print(f"Hardware Error: {e}")
                time.sleep(2)
            
    threading.Thread(target=hardware_monitor_thread, daemon=True).start()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)

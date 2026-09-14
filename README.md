| File Name | Functional Description |
| :--- | :--- |
| **`bhavaani_integrated_master.py`** | Main entry point combining BLE receiver, CV engine, and alert router into an end-to-end pipeline. |
| **`bhavaani_core_engine.py`** | Base algorithm engine for threat scoring, sensor thresholding, and state management. |
| **`main_edge_processor.py`** | Primary edge processor executing frame handling, spatial velocity tracking, and threat classification. |
| **`week2_multi_frame_anomaly.py`** | OpenCV multi-frame tracking module for identifying rapid-approach threats and camera tampering. |
| **`week3_dispatch_router.py`** | Dynamic network router for fallback alerts (Webhooks  Native GSM/SMS  Emergency JSON Payload). |
| **`app_ble_receiver.py`** | BLE receiver module simulating incoming wireless sensor telemetry from the wearable unit. |
| **`app_core_dispatcher.py`** | Dispatch engine building emergency payloads (including satellite GPS data and ERSS-112 formatting). |
| **`app_user_profile.py`** | Profile management logic for loading user contacts and emergency preferences. |
| **`user_profile.json`** | JSON configuration containing sample user data, emergency contacts, and calibration metadata. |
| **`snapshot_alert.jpg`** | Sample camera frame used to demonstrate ALPR / local OCR extraction during offline testing. |

---

## ⚙️ Prerequisites & Installation

Ensure you have **Python 3.8+** installed on your system.

### 1. Clone or Download the Files
If using GitHub:
```bash
git clone [https://github.com/DaveHeet6208/Bhavaani-Kavach.git](https://github.com/DaveHeet6208/Bhavaani-Kavach.git)
cd Bhavaani-Kavach

### 2. Install the required C++ bindings and Python packages

pip install opencv-python numpy pytesseract

### 3. How to run the coding part???

python bhavaani_integrated_master.py (through the command prompt)

Expected Terminal / Window Output:

BLE Telemetry: Handshake confirmation logged with incoming RSSI metrics.

OpenCV Window: Visual window rendering motion tracking vectors, adaptive thresholding, and frame alerts.

Dispatch Verification: JSON payload printed to console showing satellite GPS strings and emergency alert routing.

### 4. To test multi-frame vision anomaly...
python week2_multi_frame_anomaly.py

### 5. To test multi-tier offline communication...
python week3_dispatch_router.py

### 6. To test BLE Receiver Logic & Hardware Handshake:
python app_ble_receiver.py


🔒 Security & Privacy Notice
All video processing, frame buffering, and optical character recognition (ALPR) execute locally on-device. 
Local buffers are maintained in a temporary 2GB encrypted FIFO cache and automatically flushed upon secure reset.


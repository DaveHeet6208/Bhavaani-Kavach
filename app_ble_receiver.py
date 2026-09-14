# app_ble_receiver.py - Real-time Bluetooth Low Energy Bridge
import asyncio
import json
import time
from bleak import BleakClient, BleakScanner
from bhavaani_integrated_master import BhavaaniMasterSystem

# UUIDs matching the ESP32-CAM BLE GATT Server
LOCKET_SERVICE_UUID = "4fa1c201-8fe3-4a05-a3c3-d0a3f0723382"
ALERT_CHARACTERISTIC_UUID = "8ba2ba7c-2ed5-4852-954d-c8077561ed13"


class BhavaaniBLEBridge:

  def __init__(self):
    self.master_system = BhavaaniMasterSystem()

  def handle_ble_notification(self, sender, data):
    """Triggered automatically when the locket sends an alert packet over BLE."""
    payload_str = data.decode("utf-8")
    print("\n[BLE HARDWARE INTERCEPT] Received packet from Locket!")

    # Execute the full app pipeline using real hardware trigger
    self.master_system.execute_full_pipeline(payload_str)

  async def run_ble_listener(self):
    print("========================================================")
    print("    BHAVAANI KAVACH: BLUETOOTH RECEIVER LISTENING...   ")
    print("========================================================")
    print(" Scanning for 'BHAVAANI_KAVACH_LOCKET'...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and "BHAVAANI" in d.name
    )

    if not device:
      print(
          "\n[BLE SEARCH] Locket not found in range. (Waiting for"
          " hardware...)"
      )
      print(" Running in Standby Mode...")
      return

    print(
        f"\n[CONNECTED] Paired with device: {device.name} [{device.address}]"
    )

    async with BleakClient(device.address) as client:
      # Subscribe to emergency trigger notifications
      await client.start_notify(
          ALERT_CHARACTERISTIC_UUID, self.handle_ble_notification
      )
      print(" -> Listening for emergency motion triggers from locket...")

      # Keep listener alive
      while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
  bridge = BhavaaniBLEBridge()
  # Ensure you ran: pip install bleak
  try:
    asyncio.run(bridge.run_ble_listener())
  except KeyboardInterrupt:
    print("\nBLE Listener stopped.")

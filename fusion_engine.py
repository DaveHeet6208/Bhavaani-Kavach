import time
from collections import deque
from datetime import datetime

class FusionEngine:
    def __init__(self, base_acoustic_threshold=80.0, base_motion_threshold=1500.0, temporal_window=4.0, required_sustained_bursts=3):
        self.base_acoustic_threshold = base_acoustic_threshold
        self.base_motion_threshold = base_motion_threshold
        self.temporal_window = temporal_window
        self.required_sustained_bursts = required_sustained_bursts
        
        # History deques to track recent events (store tuples of (timestamp, value))
        self.acoustic_history = deque()
        self.motion_history = deque()
        
        # Track sustained anomalies
        self.sustained_burst_count = 0

    def _get_time_of_day_multiplier(self):
        """
        Time-of-Day Weighting: Threats are statistically higher between 8 PM - 5 AM.
        Returns a multiplier that Lowers the threshold (increases sensitivity) at night.
        """
        hour = datetime.now().hour
        if 20 <= hour or hour <= 5:
            return 0.75  # 25% more sensitive at night
        return 1.0

    def _clean_old_events(self, current_time):
        """Remove events older than the temporal window."""
        while self.acoustic_history and current_time - self.acoustic_history[0][0] > self.temporal_window:
            self.acoustic_history.popleft()
        while self.motion_history and current_time - self.motion_history[0][0] > self.temporal_window:
            self.motion_history.popleft()
            
    def process_signal(self, acoustic_db=0.0, motion_score=0.0, weapon_detected=False):
        """
        Ingest new sensor data and evaluate all layers.
        Returns (bool, str): (Trigger_Alert, Reason)
        """
        if weapon_detected:
            return True, "STATIC_WEAPON_THREAT_L5"
            
        current_time = time.time()
        
        multiplier = self._get_time_of_day_multiplier()
        current_acoustic_threshold = self.base_acoustic_threshold * multiplier
        current_motion_threshold = self.base_motion_threshold * multiplier
        
        # Layer 1: Acoustic Threshold Check
        is_acoustic_high = acoustic_db >= current_acoustic_threshold
        if is_acoustic_high:
            self.acoustic_history.append((current_time, acoustic_db))
            
        # Layer 2: Motion Threshold Check
        is_motion_high = motion_score >= current_motion_threshold
        if is_motion_high:
            self.motion_history.append((current_time, motion_score))
            
        self._clean_old_events(current_time)
        
        # Layer 3: Temporal Correlation
        # Are there both acoustic and motion spikes within the recent temporal window?
        has_temporal_correlation = len(self.acoustic_history) > 0 and len(self.motion_history) > 0
        
        # Layer 4: Sustained Duration
        # Must be correlated AND the current frame must still be anomalous
        if has_temporal_correlation and (is_acoustic_high or is_motion_high):
            self.sustained_burst_count += 1
        else:
            # If the chain breaks (even for a moment), reset the sustained counter
            self.sustained_burst_count = 0
            
        if self.sustained_burst_count >= self.required_sustained_bursts:
            # Threat verified across all 4 layers!
            # Reset history to prevent immediate re-triggering
            self.acoustic_history.clear()
            self.motion_history.clear()
            self.sustained_burst_count = 0
            return True, "THREAT_VERIFIED_L4"
            
        return False, "MONITORING"

if __name__ == "__main__":
    # Quick test of the logic
    engine = FusionEngine()
    print("Test 1: Single spike (No trigger)")
    print(engine.process_signal(acoustic_db=85, motion_score=2000)) # Burst 1
    print(engine.process_signal(acoustic_db=40, motion_score=100))  # Reset
    
    print("\nTest 2: Temporal mismatch (No trigger)")
    print(engine.process_signal(acoustic_db=85, motion_score=100))
    time.sleep(4.1) # Wait out the temporal window
    print(engine.process_signal(acoustic_db=40, motion_score=2000))
    
    print("\nTest 3: Sustained & Correlated Attack (Trigger!)")
    print(engine.process_signal(acoustic_db=85, motion_score=2000)) # Burst 1
    print(engine.process_signal(acoustic_db=85, motion_score=2000)) # Burst 2
    print(engine.process_signal(acoustic_db=85, motion_score=2000)) # Burst 3 -> Trigger!

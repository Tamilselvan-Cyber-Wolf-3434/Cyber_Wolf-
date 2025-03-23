import pandas as pd
from datetime import datetime
import os

class DetectionLogger:
    def __init__(self):
        """Initialize detection logger"""
        self.log_file = "data/detection_log.csv"
        self.columns = ['timestamp', 'target_object', 'confidence', 'location']
        
        # Create log file if it doesn't exist
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            pd.DataFrame(columns=self.columns).to_csv(self.log_file, index=False)
            
    def log_detection(self, timestamp, target_object, detections):
        """Log detection event"""
        for detection in detections:
            log_entry = {
                'timestamp': timestamp,
                'target_object': target_object,
                'confidence': detection['confidence'],
                'location': str(detection['box'])
            }
            
            # Append to CSV
            pd.DataFrame([log_entry]).to_csv(
                self.log_file,
                mode='a',
                header=False,
                index=False
            )
            
    def get_recent_logs(self, n=5):
        """Get recent detection logs"""
        try:
            df = pd.read_csv(self.log_file)
            return df.tail(n)
        except Exception:
            return pd.DataFrame(columns=self.columns)

import pygame
import threading
import time
import pyttsx3
from datetime import datetime

class AlertSystem:
    def __init__(self):
        """Initialize alert system"""
        pygame.mixer.init()
        self.is_active = False
        self.alert_thread = None
        self.speech_engine = pyttsx3.init()

    def play_alert(self):
        """Play alert sound"""
        try:
            # Using system beep as a fallback
            print('\a')
            time.sleep(1)
        except Exception as e:
            print(f"Error playing alert: {str(e)}")

    def speak_alert(self, message):
        """Speak the alert message"""
        try:
            self.speech_engine.say(message)
            self.speech_engine.runAndWait()
        except Exception as e:
            print(f"Error speaking alert: {str(e)}")

    def alert_loop(self, detected_objects=None):
        """Alert sound and speech loop"""
        while self.is_active:
            self.play_alert()
            if detected_objects:
                message = f"Alert! Detected {len(detected_objects)} objects: {', '.join(obj['class'] for obj in detected_objects)}"
                self.speak_alert(message)
            time.sleep(2)

    def trigger_alert(self, detected_objects=None):
        """Trigger alert system with optional object information"""
        if not self.is_active:
            self.is_active = True
            self.alert_thread = threading.Thread(target=self.alert_loop, args=(detected_objects,))
            self.alert_thread.daemon = True
            self.alert_thread.start()

    def stop_alert(self):
        """Stop alert system"""
        self.is_active = False
        if self.alert_thread:
            self.alert_thread.join()
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
class EmailAlert:
    def __init__(self):
        """Initialize EmailJS alert system"""
        self.emailjs_user_id = os.getenv('EMAILJS_USER_ID')
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID')
        self.emailjs_template_id = os.getenv('EMAILJS_TEMPLATE_ID')
        self.recipient_email = os.getenv('ALERT_EMAIL')
        self.enabled = all([
            self.emailjs_user_id,
            self.emailjs_service_id,
            self.emailjs_template_id,
            self.recipient_email
        ])
        
    def test_email(self):
        """Send a test email to verify EmailJS setup"""
        test_detections = [{
            'class': 'TEST',
            'confidence': 1.0
        }]
        success = self.send_alert(test_detections)
        return {
            'success': success,
            'enabled': self.enabled,
            'config': {
                'user_id': bool(self.emailjs_user_id),
                'service_id': bool(self.emailjs_service_id),
                'template_id': bool(self.emailjs_template_id),
                'recipient': bool(self.recipient_email)
            }
        }

    def send_alert(self, detections, image_path=None):
        """Send email alert using EmailJS"""
        if not self.enabled:
            print("Email alerts not configured")
            return False

        try:
            # Prepare detection information
            detected_objects = ", ".join([f"{d['class']} ({d['confidence']:.2f})" 
                                       for d in detections])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare email data
            template_params = {
                'to_email': self.recipient_email,
                'timestamp': timestamp,
                'detected_objects': detected_objects,
                'confidence': max([d['confidence'] for d in detections]),
                'location': "Main Camera",
                'additional_info': f"Total objects detected: {len(detections)}"
            }

            # Send email through EmailJS
            data = {
                'user_id': self.emailjs_user_id,
                'service_id': self.emailjs_service_id,
                'template_id': self.emailjs_template_id,
                'template_params': template_params
            }
            print(f"Sending email with data: {data}")
            
            headers = {
                'Content-Type': 'application/json',
                'origin': 'https://replit.com'
            }
            response = requests.post(
                'https://api.emailjs.com/api/v1.0/email/send',
                json=data,
                headers=headers
            )

            if response.status_code == 200:
                print(f"Email alert sent successfully")
                return True
            else:
                print(f"Failed to send email alert: Status {response.status_code}")
                print(f"Response: {response.text}")
                print(f"Request data: {json.dumps(data, indent=2)}")
                return False

        except Exception as e:
            print(f"Error sending email alert: {str(e)}")
            print(f"Error type: {type(e)}")
            return False

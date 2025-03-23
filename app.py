import streamlit as st
import cv2
import numpy as np
from utils.detection import load_model, process_frame
from utils.alert import AlertSystem
from utils.logger import DetectionLogger
import time
from datetime import datetime
import os
import glob
import csv
from PIL import Image
import io
from utils.email_alert import EmailAlert

# Page config
st.set_page_config(
    page_title="Criminal Stopper - Security System",
    page_icon="🚨",
    layout="wide"
)

# Initialize session state
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'latest_detections' not in st.session_state:
    st.session_state.latest_detections = []
if 'total_detections' not in st.session_state:
    st.session_state.total_detections = {}

# Initialize components
@st.cache_resource
def init_components():
    model = load_model()
    alert_system = AlertSystem()
    logger = DetectionLogger()
    email_alert = EmailAlert()
    return model, alert_system, logger, email_alert

model, alert_system, logger, email_alert = init_components()

# Sidebar controls
st.sidebar.title("Control Panel")
confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
target_object = st.sidebar.text_input("Target Object Name", "person")

st.sidebar.markdown("---")
st.sidebar.subheader("Custom Target Settings")
uploaded_file = st.sidebar.file_uploader("Upload Target Image", type=['png', 'jpg', 'jpeg'])
if uploaded_file is not None:
    # Convert uploaded file to image
    image_bytes = uploaded_file.read()
    target_image = Image.open(io.BytesIO(image_bytes))
    st.sidebar.image(target_image, caption="Uploaded Target", use_column_width=True)

    # Save uploaded target image
    target_path = os.path.join("targets", uploaded_file.name)
    os.makedirs("targets", exist_ok=True)
    target_image.save(target_path)
    st.session_state['custom_target'] = target_path


# Export controls
if st.sidebar.button("Export Detection Data"):
    with open('detection_export.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Object', 'Count'])
        for obj, count in st.session_state.total_detections.items():
            writer.writerow([obj, count])
    st.sidebar.success("Data exported to detection_export.csv")

st.sidebar.markdown("---")
st.sidebar.subheader("Email Alert Settings")
if not email_alert.enabled:
    st.sidebar.warning("Email alerts not configured. Please set required environment variables.")
    if st.sidebar.button("Configure Email Alerts"):
        st.sidebar.info("""
        Required environment variables:
        - EMAILJS_USER_ID
        - EMAILJS_SERVICE_ID
        - EMAILJS_TEMPLATE_ID
        - ALERT_EMAIL
        """)
else:
    st.sidebar.success("Email alerts configured")
    st.sidebar.text(f"Alerts will be sent to: {email_alert.recipient_email}")
    if st.sidebar.button("Test Email Alert"):
        result = email_alert.test_email()
        if result['success']:
            st.sidebar.success("Test email sent successfully!")
        else:
            st.sidebar.error("Failed to send test email")
            st.sidebar.json(result)

# Main content
st.title("Criminal Stopper - Security System")

# Camera selection
camera_option = st.selectbox(
    "Select Camera Source",
    options=["Demo Mode", "Webcam", "IP Camera"],
    index=0
)

camera_url = None
if camera_option == "IP Camera":
    camera_url = st.text_input("Enter IP Camera URL")
elif camera_option == "Webcam":
    camera_url = 0
else:  # Demo Mode
    st.info("Running in demo mode with sample video")
    camera_url = "sample_video.mp4"

# Create columns for layout
col1, col2 = st.columns([2, 1])

# Main video feed
with col1:
    st.subheader("Live Camera Feed")
    video_placeholder = st.empty()

# Detection info and gallery
with col2:
    st.subheader("Active Detection")
    detection_info = st.empty()

    st.subheader("Detection Statistics")
    stats_placeholder = st.empty()

    st.subheader("Recent Detections Gallery")
    gallery_placeholder = st.empty()

def get_demo_frame():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, "Demo Mode - No Camera", (50, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame

# Start camera feed
try:
    cap = cv2.VideoCapture(camera_url if camera_url is not None else 0)
    if not cap.isOpened():
        st.warning("Could not access camera. Running in demo mode.")
        demo_mode = True
    else:
        demo_mode = False
except Exception as e:
    st.warning(f"Camera error: {str(e)}. Running in demo mode.")
    demo_mode = True

# Start detection loop
try:
    while True:
        if demo_mode:
            frame = get_demo_frame()
            ret = True
        else:
            ret, frame = cap.read()
            if not ret:
                st.error("Error: Could not access camera feed")
                frame = get_demo_frame()

        # Process frame
        processed_frame, detections = process_frame(
            frame, 
            model, 
            target_object, 
            confidence_threshold,
            custom_target_path=st.session_state.get('custom_target', None)
        )

        # Update frame counter and statistics
        st.session_state.frame_count += 1
        for detection in detections:
            obj_class = detection['class']
            if obj_class not in st.session_state.total_detections:
                st.session_state.total_detections[obj_class] = 0
            st.session_state.total_detections[obj_class] += 1

        # Calculate FPS
        elapsed_time = time.time() - st.session_state.start_time
        fps = st.session_state.frame_count / elapsed_time

        # Display processed frame
        video_placeholder.image(
            processed_frame, 
            channels="BGR",
            use_container_width=True
        )

        # Handle detections
        if detections:
            alert_system.trigger_alert(detections)
            timestamp = datetime.now()
            logger.log_detection(timestamp, target_object, detections)
            st.session_state.latest_detections = detections

            # Save detection image
            detection_path = f"detections/{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            os.makedirs("detections", exist_ok=True)
            cv2.imwrite(detection_path, processed_frame)

            # Send email alert
            email_alert.send_alert(detections, detection_path)

        # Update detection info
        with detection_info.container():
            st.markdown(f"""
            ### System Status
            - FPS: {fps:.2f}
            - Target: {target_object}
            - Confidence: {confidence_threshold}
            - Active Alerts: {alert_system.is_active}
            - Mode: {"Demo" if demo_mode else "Live"}
            """)

        # Update statistics
        with stats_placeholder.container():
            st.markdown("### Object Counts")
            for obj, count in st.session_state.total_detections.items():
                st.markdown(f"- {obj}: {count}")

        # Display recent detection images
        detection_files = glob.glob("detections/*.jpg")
        if detection_files:
            detection_files.sort(key=os.path.getctime, reverse=True)
            latest_files = detection_files[:4]

            for img_path in latest_files:
                img = cv2.imread(img_path)
                if img is not None:
                    st.image(img, channels="BGR", use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
finally:
    if 'cap' in locals() and not demo_mode:
        cap.release()
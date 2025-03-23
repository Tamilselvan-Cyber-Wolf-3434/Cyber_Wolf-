
import cv2
import numpy as np
from ultralytics import YOLO

def load_model():
    """Load YOLO model"""
    model = YOLO('yolov5s.pt')
    return model

def process_frame(frame, model, target_object=None, confidence_threshold=0.5, custom_target_path=None):
    """Process a frame and return detections"""
    try:
        # Get predictions
        results = model(frame, verbose=False)
        detections = []

        # Process results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf > confidence_threshold:
                    cls = int(box.cls[0])
                    label = model.names[cls]
                    if target_object and label.lower() != target_object.lower():
                        continue

                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, xyxy)

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'{label} {conf:.2f}', 
                               (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 
                               0.9, (0, 255, 0), 2)

                    detections.append({
                        'class': label,
                        'confidence': conf,
                        'box': [x1, y1, x2, y2]
                    })

        return frame, detections

    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        return frame, []

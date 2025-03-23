pip install streamlit opencv-python-headless ultralytics numpy pandas pygame pyttsx3 torch Pillow
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage Guide

1. **Starting the System**:
   - Launch the application using `streamlit run app.py`
   - Select your preferred camera source from the dropdown menu

2. **Configuring Detection**:
   - Adjust the confidence threshold using the slider
   - Set the target object name (default: "person")
   - Upload custom target images for specific detection
   - Monitor the live feed and detection statistics

3. **Custom Target Detection**:
   - Click "Upload Target Image" in the sidebar
   - Select a PNG or JPEG image of your target
   - The system will automatically compare detected objects with your target

4. **Managing Alerts**:
   - Automatic audio and visual alerts when objects are detected
   - Voice announcements of detected objects
   - Export detection data using the "Export Detection Data" button

5. **Viewing Results**:
   - Real-time camera feed with detection boxes


## Email Alert Configuration

1. **Set Up EmailJS Account**:
   - Create an account at [EmailJS](https://www.emailjs.com)
   - Create a new email service
   - Create an email template

2. **Configure Environment Variables**:
   Set the following environment variables in your Repl:
   - `EMAILJS_USER_ID`: Your EmailJS User ID
   - `EMAILJS_SERVICE_ID`: Your EmailJS Service ID
   - `EMAILJS_TEMPLATE_ID`: Your EmailJS Template ID
   - `ALERT_EMAIL`: Recipient email address for alerts

3. **Test Configuration**:
   - Click "Test Email Alert" in the sidebar
   - Check the success/failure status
   - Verify receipt of test email

4. **Customizing Alerts**:
   - Alerts are sent automatically when objects are detected
   - Each alert includes timestamp, detected objects, and confidence levels
   - Template can be customized in `templates/emailjs_template.html`


   - Detection statistics and counts
   - Recent detections gallery
   - Detection logs in CSV format

## Future Features

- Multi-camera support for simultaneous monitoring
- Night vision enhancement for low-light conditions
- Facial recognition integration
- Advanced motion tracking
- Custom alert configurations
- Enhanced target matching algorithms

## Project Structure

```
├── app.py              # Main application file
├── utils/
│   ├── alert.py       # Alert system implementation
│   ├── detection.py   # Object detection utilities
│   └── logger.py      # Logging functionality
├── data/              # Detection logs and data
├── targets/           # Custom target images
└── detections/        # Saved detection images
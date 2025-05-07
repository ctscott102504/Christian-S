import cv2
import numpy as np
import tensorflow as tf
import serial
import smtplib
import time

# Email credentials
EMAIL_ADDRESS = "joshadekoya5@gmail.com"
EMAIL_PASSWORD = "zavm dxgx yjwd udnm"
TO_NUMBER = "8158226319@vtext.com"

# Connect to Arduino
ser = serial.Serial("COM3", 9600, timeout=1)
time.sleep(2)

# Load the Teachable Machine model
model_path = "C:/Users/ljgib/Downloads/proj2converted_keras/keras_model.h5"
model = tf.keras.models.load_model(model_path, compile=False)

# Setup camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 10)

def preprocess_frame(frame):
    img = cv2.resize(frame, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32) / 255.0
    return img

def send_alert():
    subject = "INTRUDER ALERT!"
    body = "Motion detected and face not recognized!"
    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_NUMBER, message)

    print("📱 Alert Sent!")

# ========== MAIN LOOP ==========
while True:
    try:
        line = ser.readline().decode("utf-8").strip()
       
        if "INTRUDER ALERT!" in line:
            print("🚨 Motion detected! Scanning face...")

            found_face = False
            recognized = False
            scan_start = time.time()

            while time.time() - scan_start < 7:  # Scan for ~7 seconds
                ret, frame = cap.read()
                frame = cv2.resize(frame, (320, 240))
                processed = preprocess_frame(frame)
                preds = model.predict(processed)
               
                class_index = np.argmax(preds)
                confidence = np.max(preds)

                if class_index == 1 and confidence >= 0.7:
                    recognized = True
                    print(f"✅ Recognized! Class: {class_index}, Confidence: {confidence:.2f}")
                    if ser and ser.is_open:
                        ser.write(b'B')  # Send to Arduino
                    break
                elif confidence < 0.7 or class_index == 0:
                    print(f"❌ Unrecognized. Class: {class_index}, Confidence: {confidence:.2f}")
                    if ser and ser.is_open:
                        ser.write(b'R')
                    found_face = True  # Still a face, just unrecognized

                cv2.imshow("Face Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # If after scanning we didn't recognize
            if not recognized:
                print("👤 Face NOT recognized! Sending SMS alert.")
                send_alert()

            time.sleep(5)  # Cooldown before next detection

        elif "All Clear" in line:
            print("✅ Room is clear.")

    except Exception as e:
        print(f"Error: {e}")
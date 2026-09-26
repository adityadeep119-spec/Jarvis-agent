import cv2
import time

print("* Center your face in front of the camera...")
cap = cv2.VideoCapture(0)
time.sleep(1.5)  # Warm up sensor exposure

ret, frame = cap.read()
cap.release()

if ret:
    cv2.imwrite("master_face.jpg", frame)
    print("* Master face profile saved to master_face.jpg successfully!")
else:
    print("Error: Could not access optical sensor.")
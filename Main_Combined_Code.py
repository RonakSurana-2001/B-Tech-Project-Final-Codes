import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
import firebase_admin
from firebase_admin import credentials, db
# Initialize the Firebase Admin SDK with your service account key
cred = credentials.Certificate('/home/rpi/Desktop/Motor_Run/testfile/myapp-e106a-firebase-adminsdk-gl9uq-a62990e6c3.json')
firebase_admin.initialize_app(cred)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
In1, In2=3,5
In3, In4=11,13
cam = cv2.VideoCapture(0)
#GPIO.setup(Ena1, GPIO.OUT)
GPIO.setup(In1, GPIO.OUT)
GPIO.setup(In2, GPIO.OUT)

#GPIO.setup(Ena2, GPIO.OUT)
GPIO.setup(In3, GPIO.OUT)
GPIO.setup(In4, GPIO.OUT)

#GPIO.output(Ena1,GPIO.HIGH)
#GPIO.output(Ena2,GPIO.HIGH)

pwm1=GPIO.PWM(In1,100)
pwm1.start(0)

pwm2=GPIO.PWM(In2,100)
pwm2.start(0)

pwm3=GPIO.PWM(In3,100)
pwm3.start(0)

pwm4=GPIO.PWM(In4,100)
pwm4.start(0)

ref = db.reference('/')
speed=ref.child("speed").get()
direction=ref.child("direction").get()

while True:
    reference_images = {
        "Pic_1": cv2.imread('/home/rpi/Desktop/Pic_1.png', cv2.IMREAD_GRAYSCALE),
        "Pic_2": cv2.imread('/home/rpi/Desktop/Pic_2.png', cv2.IMREAD_GRAYSCALE),
        "Pic_3": cv2.imread('/home/rpi/Desktop/Pic_3.png', cv2.IMREAD_GRAYSCALE)
        # Add more reference images as needed
    }
    # Initiali# No Comment ze the ORB detector
    orb = cv2.ORB_create()

   
    ret, camera_frame = cam.read()
    dicto = {"Pic_1": "Rin", "Pic_2": "Ariel", "Pic_3": "Tide"}

    # Preprocess the camera frame
    gray_camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)

    # Flag to track if a match is found
    match_found = False

    # Iterate over reference images
    for key, reference_image in reference_images.items():
        # Find keypoints and descriptors in the camera frame and reference image
        kp1, des1 = orb.detectAndCompute(gray_camera_frame, None)
        kp2, des2 = orb.detectAndCompute(reference_image, None)

        # Perform feature matching
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]

    if len(good_matches) >= 4:
            # Extract coordinates of keypoints from good matches
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Calculate homography matrix
        M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Draw contours or indicators on the camera frame
        if M is not None:
            h, w = reference_image.shape
            template_corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
            transformed_corners = cv2.perspectiveTransform(template_corners, M)
            cv2.polylines(camera_frame, [np.int32(transformed_corners)], True, (0, 255, 0), 2)

                # Update Firebase database or perform any other action
        base = ref.child("Products").get()
        x = base[dicto[key]] + 1
        print(x, dicto[key])
        result1 = ref.child("Products").update({dicto[key]: x})

                # Set match_found to True
        match_found = True

        # Print a message based on whether a match is found
        if match_found:
            print("Match found!")
        else:
            print("No match found.")

        # Display the camera frame
        #cv2.imshow('Camera Feed', camera_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
   
    speed=ref.child("speed").get()
    direction=ref.child("direction").get()
    print(speed,direction)
    if direction==0 or speed==0:#not running initial
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
        pwm3.ChangeDutyCycle(0)
        pwm4.ChangeDutyCycle(0)
    else:
        if direction=="1":#left
            pwm1.ChangeDutyCycle(speed)
            pwm2.ChangeDutyCycle(0)
            pwm3.ChangeDutyCycle(0)
            pwm4.ChangeDutyCycle(0)
        elif direction=="2":#right
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            pwm3.ChangeDutyCycle(speed)
            pwm4.ChangeDutyCycle(0)
        elif direction=="3":#Forward
            pwm1.ChangeDutyCycle(speed)
            pwm2.ChangeDutyCycle(0)
            pwm3.ChangeDutyCycle(speed)
            pwm4.ChangeDutyCycle(0)
        elif direction=="4":#backward
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(speed)
            pwm3.ChangeDutyCycle(0)
            pwm4.ChangeDutyCycle(speed)
cam.release()
GPIO.cleanup() 

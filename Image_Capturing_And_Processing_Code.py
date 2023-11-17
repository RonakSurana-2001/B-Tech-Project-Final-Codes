import cv2
import numpy as np
import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials, db
import picamera

cred = credentials.Certificate('/home/rpi/Desktop/Motor_Run/testfile/myapp-e106a-firebase-adminsdk-gl9uq-a62990e6c3.json')

# Initialize Firebase app
firebase_admin.initialize_app(cred)

# Create a reference to the root of your database
ref = db.reference('/')
# Load the target image (product in a different color box)
camera=picamera.PiCamera()
camera.capture('/home/rpi/Desktop/target_image.png')
target_image = cv2.imread('/home/rpi/Desktop/target_image.png', cv2.IMREAD_GRAYSCALE)

dicto={"Pic_1":"Rin","Pic_2":"Ariel","Pic_3":"Tide"}

for i in range(1,4):
    # Load the template image (one of the products in a different color box)
    pic_i_value = "Pic_"+str(i)
    template_image = cv2.imread(f'/home/rpi/Desktop/{pic_i_value}.png', cv2.IMREAD_GRAYSCALE)
    # Initialize the ORB detector
    orb = cv2.ORB_create()
    # Find keypoints and descriptors in the template and target images
    kp1, des1 = orb.detectAndCompute(template_image, None)
    kp2, des2 = orb.detectAndCompute(target_image, None)
    # Check if descriptors are empty
    if des1 is None or des2 is None:
        print("No descriptors found in one of the images.")
    else:
        # Convert descriptors to CV_32F if needed
        if des1.dtype != np.float32:
            des1 = des1.astype(np.float32)
        if des2.dtype != np.float32:
            des2 = des2.astype(np.float32)
        # Create a BFMatcher (Brute Force Matcher) and perform matching
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        # Apply ratio test to select good matches
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
        if len(good_matches)>=4:
            # Create a copy of the target image to draw contours on
            target_with_contours = target_image.copy()
            # Extract coordinates of keypoints from good matches
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            # Calculate the homography matrix
            M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            # Get the dimensions of the template image
            h, w = template_image.shape
            # Define the four corners of the template image
            template_corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
            # Transform the corners to the perspective of the target image
            transformed_corners = cv2.perspectiveTransform(template_corners, M)
            # Draw a contour around the detected object
            cv2.polylines(target_with_contours, [np.int32(transformed_corners)], True, 255, 3, cv2.LINE_AA)
            # Create a resizable window and display the matched image with contours
            #cv2.namedWindow('Matched Image with Contours', cv2.WINDOW_NORMAL)
            #cv2.resizeWindow('Matched Image with Contours', 800, 600)  # Replace with your desired width and height
            #cv2.imshow('Matched Image with Contours', target_with_contours)
            base=ref.child("Products").get()
            x=base[dicto[pic_i_value]]+1
            print(x,dicto[pic_i_value])
            result1 = ref.child("Products").update({dicto[pic_i_value]: x})
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Not enough good matches. Skipping update.")
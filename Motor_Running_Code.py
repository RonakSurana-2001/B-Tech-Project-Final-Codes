import RPi.GPIO as GPIO
from time import sleep
import firebase_admin
from firebase_admin import credentials, db

# Initialize the Firebase Admin SDK with your service account key
cred = credentials.Certificate('/home/rpi/Desktop/Motor_Run/testfile/myapp-e106a-firebase-adminsdk-gl9uq-a62990e6c3.json')
firebase_admin.initialize_app(cred)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
Ena1, In1, In2 = 3, 5, 7
Ena2, In3, In4 = 11, 13, 15

GPIO.setup(Ena1, GPIO.OUT)
GPIO.setup(In1, GPIO.OUT)
GPIO.setup(In2, GPIO.OUT)

GPIO.setup(Ena2, GPIO.OUT)
GPIO.setup(In3, GPIO.OUT)
GPIO.setup(In4, GPIO.OUT)

GPIO.output(Ena1, GPIO.HIGH)
GPIO.output(Ena2, GPIO.HIGH)

pwm1 = GPIO.PWM(Ena1, 100)
pwm1.start(0)

pwm2 = GPIO.PWM(Ena2, 100)
pwm2.start(0)

ref = db.reference('/')
speed = ref.child("speed").get()
direction = ref.child("direction").get()

GPIO.output(In1, GPIO.LOW)
GPIO.output(In2, GPIO.LOW)
GPIO.output(In3, GPIO.LOW)
GPIO.output(In4, GPIO.LOW)

while True:
    speed = ref.child("speed").get()
    direction = ref.child("direction").get()
    if direction == 0 or speed == 0:  # not running initially
        GPIO.output(In1, GPIO.LOW)
        GPIO.output(In2, GPIO.LOW)
        GPIO.output(In3, GPIO.LOW)
        GPIO.output(In4, GPIO.LOW)
        pwm1.ChangeDutyCycle(speed)
        pwm2.ChangeDutyCycle(speed)
    else:
        if direction == "1":  # left
            GPIO.output(In1, GPIO.HIGH)
            GPIO.output(In2, GPIO.LOW)
            GPIO.output(In3, GPIO.LOW)
            GPIO.output(In4, GPIO.LOW)
            pwm1.ChangeDutyCycle(speed)
        elif direction == "2":  # right
            GPIO.output(In1, GPIO.LOW)
            GPIO.output(In2, GPIO.LOW)
            GPIO.output(In3, GPIO.HIGH)
            GPIO.output(In4, GPIO.LOW)
            pwm1.ChangeDutyCycle(speed)
        elif direction == "3":  # Forward
            GPIO.output(In1, GPIO.HIGH)
            GPIO.output(In2, GPIO.LOW)
            GPIO.output(In3, GPIO.HIGH)
            GPIO.output(In4, GPIO.LOW)
            pwm1.ChangeDutyCycle(speed)
        elif direction == "4":  # backward
            GPIO.output(In1, GPIO.LOW)
            GPIO.output(In2, GPIO.HIGH)
            GPIO.output(In3, GPIO.LOW)
            GPIO.output(In4, GPIO.HIGH)
            pwm1.ChangeDutyCycle(speed)
        else:
            exit()

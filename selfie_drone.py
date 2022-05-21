from djitellopy import Tello
import cv2
import time

import mediapipe as mp
from joblib import load

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

clf = load('gestures.joblib')

lm = []
r = ""
moving = False
frame_count = 0

######################################################################
width = 320  # WIDTH OF THE IMAGE
height = 240  # HEIGHT OF THE IMAGE
Fly = True # To control if you want to drone to take off or not
######################################################################

# CONNECT TO TELLO
tello = Tello()
tello.connect()

tello.for_back_velocity = 0
tello.left_right_velocity = 0
tello.up_down_velocity = 0
tello.yaw_velocity = 0
tello.speed = 0


print(tello.get_battery())

tello.streamoff()
tello.streamon()

if Fly:
    tello.takeoff()

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while True:

        # GET THE IMGAE FROM TELLO
        frame_read = tello.get_frame_read()
        image = frame_read.frame


        ####################################################
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                # Gesture Recognition
                data = hand_landmarks

                lm = []
                r = ""
                if data:
                    for p in range(21):
                        lm.append(data.landmark[p].x)
                        lm.append(data.landmark[p].y)
                        lm.append(data.landmark[p].z)
                
                    r = clf.predict([lm])[0]

        ####################################################
        img = cv2.resize(image, (width, height))

        if r:
            cv2.putText(img, r, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1, cv2.LINE_AA)


        if Fly:
            if not moving:
                if r=='5F':
                    if tello.send_rc_control:
                        tello.send_rc_control(0, -20, 0, 0)
                    else:
                        tello.move_back(30)
                    moving = True
                elif r=='5B':
                    if tello.send_rc_control:
                        tello.send_rc_control(0, 20, 0, 0)
                    else:
                        tello.move_forward(30)
                    moving = True
                elif r=='2':
                    cv2.imwrite(f"{time.time()}.jpg",image)
                    moving = True
                else:
                    if tello.send_rc_control:
                        tello.send_rc_control(0, 0, 0, 0)
                    moving = True         
            else:
                frame_count += 1
            
            if frame_count > 100:
                moving = False
                frame_count = 0

        # DISPLAY IMAGE
        cv2.imshow("Drone View", img)

        # WAIT FOR THE 'ESC' BUTTON TO STOP
        if cv2.waitKey(5) & 0xFF == 27:
            tello.land()
            cv2.destroyAllWindows()
            break
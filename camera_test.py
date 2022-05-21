from djitellopy import Tello
import cv2
import time

######################################################################
width = 320  # WIDTH OF THE IMAGE
height = 240  # HEIGHT OF THE IMAGE
######################################################################

message = ""
frame_count = 0

# CONNECT TO TELLO
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

print(me.get_battery())

me.streamoff()
me.streamon()

start = time.time()

while True:

    # GET THE IMGAE FROM TELLO
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))

    if frame_count >= 30:
        end = time.time()
        message = f"FPS: {frame_count/(end - start):.2f}"
        frame_count = 0
        start = end
    else:
        frame_count += 1

    cv2.putText(img, message, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 1, cv2.LINE_AA)

    # DISPLAY IMAGE
    cv2.imshow("Tello View", img)

    # WAIT FOR THE 'Q' BUTTON TO STOP
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # me.land()
        break
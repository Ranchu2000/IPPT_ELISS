import cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm
import time
import math

cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
count = 0
direction = 0
form = 0
feedback = "Begin"
countDown=0
start=False
finish= False
endPage=False
result=""
end=-1
duration=60

#Conditions:
elbowMin=65
elbowMax=165
shoulderMin= 30
shoulderMax=60
hipMin= 160
#indicators:
elbowBool= False
shoulderBool=False
hipBool=False

while cap.isOpened():
    ret, img = cap.read() #640 x 480
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    if len(lmList) != 0:
        elbow = detector.findAngle(img, 11, 13, 15)
        shoulder = detector.findAngle(img, 13, 11, 23)
        hip = detector.findAngle(img, 11, 23,25)
        
        #Percentage of success of pushup
        per = np.interp(elbow, (elbowMin, elbowMax), (0, 100))
        
        #Bar to show Pushup progress
        bar = np.interp(elbow, (elbowMin, elbowMax), (380, 50))

        #Check to ensure right form before starting the program
        if (shoulder<shoulderMax):
            shoulderBool=False
        else:
            shoulderBool=True
        if (hip <hipMin):
            hipBool= False
        else:
            hipBool=True
        if (elbow<elbowMax):
            elbowBool= False
        else:
            elbowBool=True
        
        if (shoulderBool==True and elbowBool==True and hipBool==True and endPage==False):
            if form==0:
                form=1
                feedback = "Start"
                end= time.perf_counter()+duration
                start=True        
        if (start==True):
            countDown= end- time.perf_counter()
        if int(countDown)<0:
            result= "Final Count: "+ str(math.floor(count))
            print(result)
            finish= True

        #Check for full range of motion for the pushup
        if form == 1:
            if direction== 0:
                feedback = "Down"
                if (shoulder>shoulderMin):
                    shoulderBool=False
                else:
                    shoulderBool=True
                if (hip <hipMin):
                    hipBool= False
                else:
                    hipBool=True
                if (elbow>elbowMin):
                    elbowBool= False
                else:
                    elbowBool=True
                if (shoulderBool==True and elbowBool==True and hipBool==True):
                    count += 0.5
                    direction = 1

            if direction == 1:
                feedback = "Up"
                if (shoulder<shoulderMax):
                    shoulderBool=False
                else:
                    shoulderBool=True
                if (hip<hipMin):
                    hipBool= False
                else:
                    hipBool=True
                if (elbow<elbowMax):
                    elbowBool= False
                else:
                    elbowBool=True
                if (shoulderBool==True and elbowBool==True and hipBool==True):
                    count += 0.5
                    direction = 0
        print(count)
        
        #Draw Bar
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)
        #Pushup counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (5, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        #Feedback 
        cv2.rectangle(img, (495, 0), (640, 130), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (495, 40 ), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

        specificFeedback="Shoulder: "+ str(shoulderBool) +"\n"+ "Hip: "+ str(hipBool) +"\n"+ "Elbow: "+ str(elbowBool) +"\n"
        y0, dy = 60, 20
        for i, line in enumerate(specificFeedback.split('\n')):
            y = y0 + i*dy
            cv2.putText(img, line, (495, y ), cv2.FONT_HERSHEY_SIMPLEX, .5, 2)

        cv2.putText(img, str(round(int(countDown),1)), (495, 130), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)
        if finish==True:
            cv2.rectangle(img, (0, 0), (640, 480), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, result, (50, 240), cv2.FONT_HERSHEY_PLAIN, 5,
                    (0, 255, 0), 3)
            endPage=True
            form=0
    cv2.imshow('Pushup counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
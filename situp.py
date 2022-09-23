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
shoulderBladeMin= 150
buttStart=165
buttEnd= 80
kneeMin= 120
earCupMin= 40
touchKneeMin=40
#indicators:
shoulderBool=False
buttBool= False
kneeBool= False
earCupBool= False


while cap.isOpened():
    ret, img = cap.read() #640 x 480
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        shoulderBlade= detector.findAngle(img, 7,11,29)
        butt= detector.findAngle(img, 11,23,29)
        knee= detector.findAngle(img, 23,25,29)
        earCup= detector.comparePosition(img, 7,21)
        touchKnee= detector.comparePosition(img, 13,25)

        #Percentage of success of situp
        per = np.interp(butt, (buttEnd, buttStart), (0, 100))

        #Bar to show Pushup progress
        bar = np.interp(butt, (buttEnd, buttStart), (380, 50))

        #Check to ensure right form before starting the program
        
        if (shoulderBlade<shoulderBladeMin):
            shoulderBool=False
        else:
            shoulderBool=True
        if (butt <buttStart):
            buttBool= False
        else:
            buttBool=True
        if (knee>kneeMin):
            kneeBool= False
        else:
            kneeBool=True
        if (earCup[0] >earCupMin or earCup[1]>earCupMin):
            earCupBool= False
        else:
            earCupBool=True
        
        if (shoulderBool==True and buttBool==True and kneeBool==True and earCupBool==True):
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
            #lying flat-> measure to go up
            if direction == 0:
                feedback = "Up"
                if (butt <buttEnd):
                    buttBool= False
                else:
                    buttBool=True
                if (earCup[0] >earCupMin or earCup[1]>earCupMin):
                    earCupBool= False
                else:
                    earCupBool=True
                if (touchKnee[0] >touchKneeMin or touchKnee[1]>touchKneeMin):
                    kneeBool= False
                else:
                    kneeBool=True
                if (buttBool==True and kneeBool==True and earCupBool==True):                
                    count += 0.5
                    direction = 1
            #up position-> measure to go down
            if direction==1:
                feedback = "Down"
                if (shoulderBlade<shoulderBladeMin):
                    shoulderBool=False
                else:
                    shoulderBool=True
                if (butt <buttStart):
                    buttBool= False
                else:
                    buttBool=True
                if (knee>kneeMin):
                    kneeBool= False
                else:
                    kneeBool=True
                if (earCup[0] >earCupMin or earCup[1]>earCupMin):
                    earCupBool= False
                else:
                    earCupBool=True
                if (shoulderBool==True and buttBool==True and kneeBool==True and earCupBool==True):                
                    count += 0.5
                    direction = 0
    
        print(count)
        
        #Draw Bar
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)
        #Situp counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        #Feedback 
        cv2.rectangle(img, (500, 0), (640, 130), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (500, 40 ), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

        specificFeedback="Shoulder: "+ str(shoulderBool) +"\n"+ "Butt: "+ str(buttBool) +"\n"+ "Knee: "+ str(kneeBool) +"\n"+ "EarCup: "+ str(earCupBool) +"\n"

        y0, dy = 50, 20
        for i, line in enumerate(specificFeedback.split('\n')):
            y = y0 + i*dy
            cv2.putText(img, line, (500, y ), cv2.FONT_HERSHEY_SIMPLEX, .5, 2)
       
        cv2.putText(img, str(round(int(countDown),1)), (495, 130), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)
        
        if finish==True:
            cv2.rectangle(img, (0, 0), (640, 480), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, result, (50, 240), cv2.FONT_HERSHEY_PLAIN, 5,
                    (0, 255, 0), 3)
            endPage=True
            form=0

    cv2.imshow('Situp counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
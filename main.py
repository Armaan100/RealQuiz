import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from questions import data_me as data
import time

detector = HandDetector(detectionCon=0.8, maxHands=1)
print(len(data))

width = 1280
height = 720

# cvzone set up
cap = cv2.VideoCapture(0)
cap.set(3, width)  #set width
cap.set(4, height)   #set height

#Initialize pos
question_x = 200
question_y = 100

option1_x = 200
option1_y = 200

option2_x = 700
option2_y = 200

option3_x = 200
option3_y = 350

option4_x = 700
option4_y = 350


#Circles
circles = []
circle_y = 550
circle_x_incr = 50
circleAddStatus = True


# data: [<question>, <option1>, <option2>, <option3>, <option4>, <choice5>, <answer>]
# A MCQ Object Structure
class MCQ():
    def __init__(self, curr_data):
        self.question = curr_data[0]
        self.option1 = curr_data[1]
        self.option2 = curr_data[2]
        self.option3 = curr_data[3]
        self.option4 = curr_data[4]
        self.answer = curr_data[5]
        
        self.player_answer = None
        

    def gameUpdate(self, x, y, bbox_list):
        global circles, circle_x_incr, circle_y, circleAddStatus
        for i, bbox in enumerate(bbox_list):
            x1, y1, x2, y2 = bbox
            if x1 < x < x2 and y1 < y < y2:
                self.player_answer = i+1
                if self.player_answer == self.answer:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0 ,200, 0), cv2.FILLED)
                    color = (0, 255, 0) #Green Color for right choice
                else:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (200, 0, 0), cv2.FILLED)
                    color = (0, 0, 255) #Red Color for wrong choice
                
                if circleAddStatus:
                    circles.append(((0 + circle_x_incr, circle_y), color))
                    answer_selected_time = time.time()  # Record the time when the answer is selected
                    circleAddStatus = False  # Set the flag
                    print(f"Answer selected at {answer_selected_time}")


# MCQ Props
background_color = (255, 255, 255)
google_green = (52, 168, 83)
google_blue = (66, 133, 244)
google_yellow = (244, 180, 0)
google_red = (219, 68, 55)
google_black = (0, 0, 0)

# MCQ Object Creation
list_mcq = []
for data in data:
    list_mcq.append(MCQ(data))

# print(len(list_mcq))

#Intialize question number
question_num = 0
total_question = len(list_mcq)


#Initialize time
answer_selected_time = None

start = True

while start:
    # Capture and Process Frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)            
    
    
    if question_num < total_question:
        mcq = list_mcq[question_num]
        
        img, bbox1  = cvzone.putTextRect(img, list_mcq[question_num].question, (question_x, question_y), scale=2, thickness=2, colorR=background_color, colorT=google_black, offset=5, border=1)
        img, bbox2  = cvzone.putTextRect(img, list_mcq[question_num].option1, (option1_x, option1_y), scale=3, thickness=2, colorR=background_color, colorT=google_blue, offset=10, border=1)
        img, bbox3  = cvzone.putTextRect(img, list_mcq[question_num].option2, (option2_x, option2_y), scale=3, thickness=2, colorR=background_color, colorT=google_green, offset=10, border=1)
        img, bbox4  = cvzone.putTextRect(img, list_mcq[question_num].option3, (option3_x, option3_y), scale=3, thickness=2, colorR=background_color, colorT=google_blue, offset=10, border=1)
        img, bbox5  = cvzone.putTextRect(img, list_mcq[question_num].option4, (option4_x, option4_y), scale=3, thickness=2, colorR=background_color, colorT=google_red, offset=10, border=1)
    
        if hands:
            hand = hands[0]
            lmList = hand['lmList']
        
            # Index finger tip
            index_tip = lmList[8]
        
            # Other finger tips
            thumb_tip = lmList[4]
            middle_tip = lmList[12]
            ring_tip = lmList[16]
            pinky_tip = lmList[20]
        
            # Check if only the index finger is raised
            if (index_tip[1] < thumb_tip[1] and
                index_tip[1] < middle_tip[1] and
                index_tip[1] < ring_tip[1] and
                index_tip[1] < pinky_tip[1]):
                    x, y, _ = hand['lmList'][8]
                    # print(x)
                    mcq.gameUpdate(x, y, [bbox2, bbox3, bbox4, bbox5])
                    if mcq.player_answer is not None:
                        answer_selected_time = time.time()
                        print(f"Answer selected at {answer_selected_time}")
    else:
        start = False
                        
    #Check if time required wait happened or not
    if answer_selected_time and time.time() - answer_selected_time > 0.3:
        print(f"Check: {time.time() - answer_selected_time}")
        question_num += 1
        circle_x_incr += 120 
        circleAddStatus = True
        answer_selected_time = None
        print(f"Moving to question {question_num}")
                        
    # Circles showing right or wrong answer
    
    for circle_center, color in circles:
        cv2.circle(img, circle_center, 30, color, cv2.FILLED)

    
    cv2.imshow("Img", img)
    cv2.waitKey(1)



# Left to do:   i) Score with End Screen    ii) Starting screen with Instructions   iii) Correct placement of the right / wrong balls

import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from questions import data as data
import time
import pygame

detector = HandDetector(detectionCon=0.8, maxHands=1)

width = 1280
height = 720

logo = cv2.imread('./Resources/logo2.png', cv2.IMREAD_UNCHANGED)

logo = cv2.resize(logo, (100, 100))
# cvzone set up
cap = cv2.VideoCapture(0)
cap.set(3, width)  #set width
cap.set(4, height)   #set height

#Initialize pos
question_x = 10
question_y = 200

option1_x = 100
option1_y = 300

option2_x = 800
option2_y = 300

option3_x = 100
option3_y = 400

option4_x = 800
option4_y = 400

logo_x = 500
logo_y = 350

#Circles
circles = []
circle_y = 550
circle_x_incr = 30
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
        global circles, circle_x_incr, circle_y, circleAddStatus, score
        for i, bbox in enumerate(bbox_list):
            x1, y1, x2, y2 = bbox
            if x1 < x < x2 and y1 < y < y2:
                self.player_answer = i+1
                if self.player_answer == self.answer:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
                    color = (0, 255, 0) #Green Color for right choice
                else:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), cv2.FILLED)
                    color = (0, 0, 255) #Red Color for wrong choice
                
                if circleAddStatus:
                    circles.append(((5 + circle_x_incr, circle_y), color))
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


#backgroung image load
background_img = cv2.imread('./Resources/final_background.jpg')

#Ending
def endScreen(score):
    # Copy the background image to img
    img = cv2.resize(background_img, (width, height))

    # Overlay the score text on the img
    text1 = f"Your Score Is: {score}"
    text2 = f"Thank you for playing!"
    pos1 = (int(width/2)-150, int(height/2))  # Bottom-left corner of the text string in the image
    pos2 = (int(width/2 - 200), int(height/2 + 50))
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1
    color = (255, 255, 255)  # Black color in BGR
    thickness = 3
    cv2.putText(img, text1, pos1, font, font_scale, color, thickness, cv2.LINE_AA)
    cv2.putText(img, text2, pos2, font, font_scale, color, thickness, cv2.LINE_AA)

    # Display the img with the background and score
    cv2.imshow("Quiz Game", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def overlay_image(img, logo, x, y):
    img[y:y + logo.shape[0], x:x + logo.shape[1]] = logo

# print("Enter category you want to play: ", end='', flush=True)
# ask_data = int(input())

# MCQ Object Creation
list_mcq = []
for data in data:
    list_mcq.append(MCQ(data))
    
#Split Text
def split_text(text, max_char_per_line=30):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_char_per_line:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    lines.append(current_line.strip())
    return lines



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
        
        # Display the question with split text
        question_text = mcq.question
        question_lines = split_text(question_text, max_char_per_line=70)

        current_y = question_y
        for line in question_lines:
            img, _ = cvzone.putTextRect(img, line, (question_x, current_y), scale=2, thickness=2, colorR=background_color, colorT=google_black, offset=5, border=1)
            current_y += 40

        # Display the options
        img, bbox2 = cvzone.putTextRect(img, mcq.option1, (option1_x, option1_y), scale=3, thickness=2, colorR=background_color, colorT=google_blue, offset=10, border=1)
        img, bbox3 = cvzone.putTextRect(img, mcq.option2, (option2_x, option2_y), scale=3, thickness=2, colorR=background_color, colorT=google_green, offset=10, border=1)
        img, bbox4 = cvzone.putTextRect(img, mcq.option3, (option3_x, option3_y), scale=3, thickness=2, colorR=background_color, colorT=google_blue, offset=10, border=1)
        img, bbox5 = cvzone.putTextRect(img, mcq.option4, (option4_x, option4_y), scale=3, thickness=2, colorR=background_color, colorT=google_red, offset=10, border=1)
    
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
        #score
        score = 0
        for mcq in list_mcq:
            if mcq.player_answer == mcq.answer:
                score+=1
        print("Score", score)
        
        endScreen(score)
        
        start = False
                        
    #Check if time required wait happened or not
    if answer_selected_time and time.time() - answer_selected_time > 0.15:
        print(f"Check: {time.time() - answer_selected_time}")
        circle_x_incr += 120 
        circleAddStatus = True
        question_num += 1
        answer_selected_time = None
        print(f"Moving to question {question_num}")
                        
    # Circles showing right or wrong answer
    
    for circle_center, color in circles:
        cv2.circle(img, circle_center, 30, color, cv2.FILLED)

    # Define the position where you want to place the logo
    overlay_image(img, logo, logo_x, logo_y)

    
        
    
    cv2.imshow("Quiz Game", img)
    cv2.waitKey(1)



# Left to do:   i) Score with End Screen    ii) Starting screen with Instructions   iii) Correct placement of the right / wrong balls

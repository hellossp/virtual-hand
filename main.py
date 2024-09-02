import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import numpy as np
from time import sleep
from pynput.keyboard import Controller

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["CLEAR", "BACKSPACE"]]

finalText = ''

keyboard = Controller()

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
        if button.text in ["CLEAR", "BACKSPACE"]:
            fontScale = 1
            thickness = 2
        else:
            fontScale = 4
            thickness = 3
        textSize = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, fontScale, thickness)[0]
        textX = x + (w - textSize[0]) // 2
        textY = y + (h + textSize[1]) // 2
        cv2.putText(img, button.text, (textX, textY), cv2.FONT_HERSHEY_PLAIN, fontScale, (255, 255, 255), thickness)
    return img

def drawTextBar(img, text, barPos=(50, 650), barSize=(1280, 85)):
    x, y = barPos
    w, h = barSize
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

class Button():
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []

shiftAmount = 115

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonSize = (100, 85) if key in ["CLEAR", "BACKSPACE"] else (85, 85)
        if key not in ["CLEAR", "BACKSPACE"]:
            buttonList.append(Button([j * 100 + 50 + shiftAmount, 100 * i + 50], key, size=buttonSize))
        else:
            buttonList.append(Button([j * 100 + 50, 100 * i + 50], key, size=buttonSize))

buttonList[-2].pos[0] += 460
buttonList[-1].pos[0] += 560

buttonPress = {button.text: False for button in buttonList}

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    allHands, img = detector.findHands(img)
    img = drawAll(img, buttonList)

    if len(allHands) != 0:
        lmList, bboxInfo = allHands[0]['lmList'], allHands[0]['bbox']
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                if button.text in ["CLEAR", "BACKSPACE"]:
                    fontScale = 1
                    thickness = 2
                else:
                    fontScale = 4
                    thickness = 3

                textSize = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, fontScale, thickness)[0]
                textX = x + (w - textSize[0]) // 2
                textY = y + (h + textSize[1]) // 2
                cv2.putText(img, button.text, (textX, textY), cv2.FONT_HERSHEY_PLAIN, fontScale, (255, 255, 255), thickness)
                l = detector.findDistance(lmList[8][:2], lmList[12][:2], img)[0]

                if l < 40:
                    if button.text == "CLEAR":
                        finalText = ""
                    elif button.text == "BACKSPACE":
                        finalText = finalText[:-1]
                    else:
                        keyboard.press(button.text)
                        finalText += button.text
                    sleep(0.6)
    
    img = drawTextBar(img, finalText)

    cv2.imshow('Image', img)
    cv2.waitKey(1)

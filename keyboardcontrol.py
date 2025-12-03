import keyboard as kb
import handdetector 
import cvzone
import cv2
import time



hd = handdetector.Handinteraction()

while True:
    is_work,activate,cursor,way = hd.update()
    if kb.is_pressed('space'):
        if is_work and activate:
            if way == [-1,0]:
                print("按下A键")
                kb.send("a")
            if way == [1,0]:
                print("按下D键")
                kb.send("d")
            if way == [0,1]:
                print("按下W键")
                kb.send("w")
            if way == [0,-1]:
                print("按下S键")
                kb.send("s")
            else:
                pass
    cv2.imshow("调试",hd.img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



cv2.destroyAllWindows()
hd.cap.release()

    
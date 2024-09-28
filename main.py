import os
import pickle
from datetime import datetime
import numpy
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from PIL.ImageChops import offset
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerecognitionrealtime-3bcce-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognitionrealtime-3bcce.appspot.com"
})

bucket = storage.bucket()
# from EncodeGenerator import encodeListKnownWithIds, encodeListKnown, studentIds

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
# print(modePathList)

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encoded File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIdx = np.argmin(faceDis)
            # print("Match Index", matchIdx)

            if matches[matchIdx]:
                # print("Known Face Detected")
                # print(studentIds[matchIdx])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground=cvzone.cornerRect(imgBackground, bbox, rt = 0)
                id = studentIds[matchIdx]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Get the data
                studentInfor = db.reference(f'Students/{id}').get()
                print(studentInfor)

                # Get the image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = numpy.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)
                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfor['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now()- datetimeObject).total_seconds()
                print(secondElapsed)
                if secondElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfor['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfor['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType != 3:
                if 10<counter<20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfor['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfor['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfor['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (38, 125, 192), 1)
                    cv2.putText(imgBackground, str(studentInfor['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (38, 125, 192), 1)
                    cv2.putText(imgBackground, str(studentInfor['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (38, 125, 192), 1)
                    (w, h), _ = cv2.getTextSize(studentInfor['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfor['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (38, 125, 192), 1)
                    imgBackground[175:175+216, 909:909+216] = imgStudent
                counter += 1
                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfor = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        if not success:
            print("Error: Could not read frame from camera.")
            break
    else:
        modeType = 0
        counter = 0
    # Hiển thị ảnh
    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

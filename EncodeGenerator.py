import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerecognitionrealtime-3bcce-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognitionrealtime-3bcce.appspot.com"
})

folderImgPath = 'Images'
pathList = os.listdir(folderImgPath)
print(pathList)

imgList = []
studentIds = []

# Đọc ảnh từ thư mục
for path in pathList:
    img = cv2.imread(os.path.join(folderImgPath, path))
    if img is None:
        print(f"Error loading image: {path}")
    else:
        imgList.append(img)
        studentIds.append(os.path.splitext(path)[0])
        fileName = f'{folderImgPath}/{path}'
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
print(studentIds)


def findEncodings(imgsList):
    encodeList = []
    for img in imgsList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Chuyển ảnh sang định dạng RGB
        try:
            encode = face_recognition.face_encodings(img)[0]  # Tạo mã hóa khuôn mặt
            encodeList.append(encode)
        except IndexError:
            print(f"Face not found in image")  # In ra nếu không tìm thấy khuôn mặt
            continue

    return encodeList

print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnown)
print("Encoding complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
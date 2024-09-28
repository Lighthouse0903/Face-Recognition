import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://facerecognitionrealtime-3bcce-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "090303":
        {
            "name":"Lighthouse",
            "major":"Data Science",
            "starting_year":2021,
            "total_attendance":5,
            "standing":"G",
            "year":4.5,
            "last_attendance_time":"2024-09-23 07:23:19"
        },
    "213436":
        {
            "name":"Tobey Maguire",
            "major":"Actor",
            "starting_year":2021,
            "total_attendance":5,
            "standing":"G",
            "year":4.5,
            "last_attendance_time":"2024-09-23 07:41:19"
        },
    "234876":
        {
            "name":"Robert Downey Jr",
            "major":"Actor",
            "starting_year":2021,
            "total_attendance":9,
            "standing":"G",
            "year":5,
            "last_attendance_time":"2024-09-23 07:42:19"
        },
    "333666":
        {
            "name":"Tom Hiddleston",
            "major":"Actor",
            "starting_year":2021,
            "total_attendance":9,
            "standing":"G",
            "year":5,
            "last_attendance_time":"2024-09-23 08:41:15"
        },
    "456213":
        {
            "name":"Chris Evans",
            "major":"Actor",
            "starting_year":2021,
            "total_attendance":9,
            "standing":"G",
            "year":5,
            "last_attendance_time":"2024-09-25 07:42:19"
        },
    "963852":
        {
            "name":"Elon Musk",
            "major":"Billionaire",
            "starting_year":2021,
            "total_attendance":9,
            "standing":"G",
            "year":5,
            "last_attendance_time":"2024-05-23 07:41:20"
        },

}

for key, value in data.items():
    ref.child(key).set(value)
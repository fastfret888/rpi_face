import face_recognition
import picamera
import time
import configparser
import sqlite3


def f_encode(file):
    """ read an image file and return face encoding as numpy array """

    print("Generating face encoding...")
    try:
        image = face_recognition.load_image_file(file)
    except:
        print("Error loading image file")
        raise Exception("Not a valid image file")
    else:
        try:
            face_encoding = face_recognition.face_encodings(image)[0]
        except:
            print("Could not encode any face")
            raise Exception("No face detecctd in image")
        else:
            return face_encoding

def camtest():
    """ Preview Pi Camera with settings from config.ini """

    config = configparser.ConfigParser()
    config.read("config.ini")
    pc = config["picam"]

    camera = picamera.PiCamera()
    camera.resolution = (pc.getint("resolution_x"), pc.getint("resolution_y"))
    camera.hflip = pc.getboolean("hflip")
    camera.rotation = pc.getint("rotation")

    camera.start_preview()
    time.sleep(5)
    camera.stop_preview()
    camera.close()

def init_db():
    """ Resets database, deletes all data """

    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)

    conn.execute("DROP TABLE IF EXISTS faces")

    conn.execute(
    "CREATE TABLE faces (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, facecode array)"
    )
    conn.commit()
    conn.close()

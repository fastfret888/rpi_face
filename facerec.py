import face_recognition
import picamera
import numpy as np
import configparser
import detected

from helpers import f_encode
from time import sleep

def capture_faces(facelist, idlist):
    """ Captures a single camera frame and idenifies known faces
        Input: known face encodings [], user ids [] ***must be correctly ordered
        Output: identified face ids [], total faces found in frame (int) """

    # Get Raspberry Pi camera settings from config.ini

    config = configparser.ConfigParser()
    config.read("config.ini")
    pc = config["picam"]

    camera = picamera.PiCamera()
    camera.resolution = (pc.getint("resolution_x"), pc.getint("resolution_y"))
    camera.hflip = pc.getboolean("hflip")
    camera.rotation = pc.getint("rotation")
    output = np.empty((pc.getint("resolution_y"), pc.getint("resolution_x"), 3), dtype=np.uint8)

    # Initialize variables
    face_locations = []
    face_encodings = []

    # Camera warm-up time 
    sleep(2) 

    while True:
        print("Capturing image.")
        
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        print("Found {} faces in image.".format(len(face_locations)))
        total_faces = len(face_locations)
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it matches

        face_ids = []

        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(facelist, face_encoding)
            id = 0

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(facelist, face_encoding)
            try:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    id = idlist[best_match_index]
            except:
                id = 0
            

            #print(matches)
            print("I see someone with ID {}!".format(id))

            face_ids.append(id)

        # Update global vars
        detected.face_ids = face_ids
        detected.total_faces = total_faces

        # Break condition
        config.read("config.ini")
        capture_active = config["facerec"].getboolean("active")
        if capture_active == False:
            camera.close()
            # Reset shared global variables
            detected.total_faces = 0
            detected.face_ids.clear()
            break
        

        

# Rpi Face - Real-Time Face Recognition for Raspberry Pi

#### Description

Rpi Face is a web application that runs face recognition features on the Raspberry Pi. It utilizes the Pi Camera to continuously capture images, detect faces and recognize faces based on a user database of known faces. Output is continuously sent to a user-friendly web interface, which also allows for convenient management and configuration.


##### APPLICATION

Possible applications include basic surveillance and integration into home automation platforms.

It is NOT recommended for authentication purposes, as the algorithms are not sophisticated enough to distinguish between real persons and reproduced print or screen images


##### FUNCTIONALITY

The application runs in Raspberry OS’s native Python 3.7, making use of the face_recognition module for face encoding, detection and recognition algorithms.
The face recognition function is run as thread, which loops image capture -> face detection -> face recognition against known face database —> return total detected faces and names of recognized persons. Each cycle takes about 3 seconds on a Raspberry Pi 4 @2k resolution, which is about as “real-time” as it gets due to the hardware limitations.

A sqlite3 database is used to store user’s names along with their face encodings. An image containing a face is submitted via the web interface and pre-processed for size and orientation before being processed by the f_encode function, which outputs a 128-dimension face encoding. The face encoding is saved to the sqlite database as a numpy array using a custom sql adapter and converter. No user images are saved in the database.

The Flask framework is used to serve the web application and exchange data with the front-end, written in HTML / CSS / Javascript. The user interface implements the following features:

- Turning the face recognition thread on / off
- Polling the server every 2 seconds to display number of persons detected and names of persons recognized
- View current database entries
- Add / remove names and faces to database
- Initialize the database (delete all entries and reset)
- Configure Pi Camera properties (resolution, rotation and horizontal flip)
- Preview Pi Camera settings


##### HARDWARE TESTED

Raspberry Pi 4B
Pi Camera v2


##### DEPENDENCIES

- face_recognition
- picamera
- numpy
- flask
- PIL
- sqlite3


##### USAGE

To start the application, simply run in the terminal window:

`flask run —host 0.0.0.0`

Then access with any web browser by entering your Raspberry Pi’s local IP address at port 5000.

e.g.:

`http://192.168.1.2:5000`

NOTE: An internet connection is required to load Bootstrap framework
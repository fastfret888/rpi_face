import db
import threading
import configparser
import detected
import json

from facerec import capture_faces
from flask import Flask, flash, redirect, render_template, request, jsonify
from time import sleep
from helpers import f_encode, camtest, init_db
from PIL import Image, ImageOps
from io import BytesIO


# Configure application
app = Flask(__name__)
app.secret_key = "kdug4fuergdffkhsgdgd"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# DEFINE GLOBAL VARIABLES
# Get lists of known face encodings and ids from database
facelist = db.getfacelist()
idlist = db.getidlist()

# Reset shared global variables
detected.total_faces = 0
detected.face_ids.clear()

# make sure camera is configured "off"
config = configparser.ConfigParser()
config.read("config.ini")
config["facerec"]["active"] = "no"
with open("config.ini", "w") as f:
    config.write(f)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    """ Main Page """
    # Get capture_faces status from .ini file
    config.read("config.ini")
    capture_active = config["facerec"].getboolean("active")
    if request.method == "POST":

        # Activate / deactivate capture_faces on button push
        if request.form.get("on_off"):
            on_off = request.form.get("on_off")
            if on_off == "True":
                config["facerec"]["active"] = "yes"
                with open("config.ini", "w") as f:
                    config.write(f)

                # Flash message
                flash("Face recognition activated")

                # Start capture_faces thread
                capturethread = threading.Thread(target=capture_faces, args=(facelist, idlist))
                capturethread.start()
                sleep(3)

            elif on_off == "False":

                # Change config to end capture_faces thread
                config["facerec"]["active"] = "no"
                with open("config.ini", "w") as f:
                    config.write(f)

                # Flash message
                flash("Face recognition deactivated")
                sleep(3)

        return redirect("/")        

    else:
        return render_template("index.html", capture_active = capture_active)

@app.route("/no_of_faces")
def no_of_faces():
    """ Return current number of faces detected """

    return jsonify(faces = detected.total_faces)

@app.route("/people")
def people():
    """ Return names of people detected """

    namedict = {}

    for id in detected.face_ids:
        if not id == 0:
            name = db.getname(id)
            namedict[id]=name

    return jsonify(namedict)

@app.route("/faces", methods=["GET", "POST"])
def faces():
    """ Face Management """

    global facelist
    global idlist                

    if request.method == "POST":

        # --- Adding a new face ---
        if "add" in request.form:

            # Verify name input
            if not request.form.get("name"):
                flash("Must provide name")
                return redirect("/faces")
            else:
                name = request.form.get("name")

            # Verify file was submitted
            if not request.files["file"]:
                flash("Must provide image file")
                return redirect("/faces")
            else:
                try:
                    f = request.files["file"]
                except:
                    flash("Error uploading file")
                    return redirect("/faces")

            # Resize and rotate Image
            try:
                print("Processing Image...")
                img = Image.open(f)

                try:
                    #rotate accordingly
                    img = ImageOps.exif_transpose(img)   
                except:
                    pass

                img.thumbnail((800, 800))
                temp = BytesIO()
                img.save(temp, format="png")

            except:
                flash("Error processing image")
                return redirect("/faces")
            
            # Try to generate face encoding
            try:
                facecode = f_encode(temp)
            except:
                flash("Invalid image file or could not detect any faces")
                return redirect("/faces")

            # Add new entry to database
            try:
                db.add(name, facecode)
            except:
                flash("Database error")
                return redirect("/faces")
            else:
                flash("New face entry added")
                # Update global lists of known face encodings and ids from database
                facelist = db.getfacelist()
                idlist = db.getidlist()
                return redirect("/faces")

        # --- Removing a face entry ---
        elif "remove" in request.form:

            # Get Id to remove
            id = request.form.get("remove")

            # Remove Id from database
            try:
                db.remove(id)
            except:
                flash("Error removing face from database")
                return redirect("/faces")
            else:
                flash("Face entry removed from database")
                # Update global lists of known face encodings and ids from database
                facelist = db.getfacelist()
                idlist = db.getidlist()
                return redirect("/faces")

        # --- Initialize Database ---
        elif "initialize" in request.form:
            return redirect("/initdb")

        return redirect("/")

    else:
        users = []    
        users = db.getidnamelist()

        return render_template("faces.html", users = users)


@app.route("/initdb", methods=["GET", "POST"])
def initdb():
    """ Initialize DB """

    global facelist
    global idlist

    if request.method == "POST":

        if "cancel" in request.form:
            return redirect("/faces")

        elif "initialize" in request.form:
            try:
                init_db()
            except:
                flash("Error trying to initialize the database")
                return redirect("/initdb")
            else:
                # Update global lists of known face encodings and ids from database
                
                facelist = db.getfacelist()
                idlist = db.getidlist()
                flash("Database initialized")
                return redirect("/faces")

    else:
        return render_template("initdb.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """ Settings """

    if request.method == "POST":

        # --- Save settings to config.ini ---
        if "save" in request.form:

            config["picam"]["resolution_x"] = request.form.get("resolution_x")
            config["picam"]["resolution_y"] = request.form.get("resolution_y")
            config["picam"]["rotation"] = request.form.get("rotation")
            config["picam"]["hflip"] = request.form.get("hflip")

            with open("config.ini", "w") as f:
                config.write(f)

            flash("Camera settings saved")
            return redirect("/settings")

        # --- Run camera preview ---
        elif "test" in request.form:

            camtest()

            return redirect("/settings")

        else:
            return redirect("/settings")

    else:

        # Read Pi Cam settings
        config.read("config.ini")
        camcfg = {}
        for name,value in config.items("picam"):
            camcfg[name] = value
        print(camcfg)
        
        return render_template("settings.html", cam = camcfg)

if __name__ == "__main__":
    app.run()


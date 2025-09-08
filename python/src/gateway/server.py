import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate           
from auth_svc import access         
from storage import util            
from bson.objectid import ObjectId  # Used to query MongoDB by document ID


# Initialize Flask app
server = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI", "")
# Connect to MongoDB for video storage
# 'videos' DB stores raw video files via GridFS
# mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")


mongo_video = PyMongo(server, uri=mongo_uri + "/videos")

# Connect to MongoDB for mp3 storage
# 'mp3s' DB stores converted audio files via GridFS
# mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")
mongo_mp3 = PyMongo(server, uri=mongo_uri + "/mp3s")

# Initialize GridFS for each database
# GridFS allows storing large binary files in MongoDB
fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# Connect to RabbitMQ for task queueing
# Used to dispatch video-to-audio conversion jobs
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err



@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        print(f"Token validation failed: {err}")
        return err

    access = json.loads(access)
    print(f"Decoded token: {access}")

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            print("Incorrect number of files")
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                print(f"Upload error: {err}")
                return err

        return "success!", 200
    else:
        print("User not authorized")
        return "not authorized", 401



@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401





if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
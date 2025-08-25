from dotenv import load_dotenv
import os
import json
import tempfile
import pika
from bson.objectid import ObjectId

#Explicit import required for MoviePy v2.2.1+
#from moviepy.editor import VideoFileClip
from moviepy import VideoFileClip



# Load environment variables early to ensure all config values are available before runtime.
load_dotenv()


def start(message, fs_videos, fs_mp3s, channel):
    """
    Converts a video (stored in GridFS) to MP3 format,
    saves the audio back to GridFS, and publishes a message to RabbitMQ.

    Args:
        message (str): JSON string containing metadata, including video_fid
        fs_videos (GridFS): MongoDB GridFS instance for video files
        fs_mp3s (GridFS): MongoDB GridFS instance for MP3 files
        channel (pika.Channel): RabbitMQ channel for publishing messages
    """

    #Parse incoming message
    message = json.loads(message)

    #Fetch video file from GridFS using ObjectId
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        video_data = fs_videos.get(ObjectId(message["video_fid"]))
        tf.write(video_data.read())
        temp_video_path = tf.name  # Path to temp video file

    #Extract audio from video using MoviePy
    try:
        clip = VideoFileClip(temp_video_path)
        audio = clip.audio
    except Exception as e:
        os.remove(temp_video_path)
        raise RuntimeError(f"Failed to extract audio: {e}")

    #Define temp MP3 output path
    temp_mp3_path = os.path.join(tempfile.gettempdir(), f"{message['video_fid']}.mp3")

    #Write audio to MP3 file
    try:
        audio.write_audiofile(temp_mp3_path)
    except Exception as e:
        os.remove(temp_video_path)
        raise RuntimeError(f"Failed to write MP3 file: {e}")
    finally:
        clip.close()  #Free MoviePy resources
        os.remove(temp_video_path)  #Clean up temp video file

    #Save MP3 to GridFS
    with open(temp_mp3_path, "rb") as f:
        mp3_data = f.read()
        fid = fs_mp3s.put(mp3_data)
    os.remove(temp_mp3_path)  #Clean up temp MP3 file

    #Attach MP3 file ID to message
    message["mp3_fid"] = str(fid)

    #Publish updated message to RabbitMQ
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  #Make message persistent
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)  #Rollback MP3 save if publish fails
        return "failed to publish message"

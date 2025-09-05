import traceback
import pika, json

def upload(f, fs_videos, channel, access):
    # Attempt to store the uploaded file in GridFS
    try:
        print(f"Storing file: {f.filename}")
        fid = fs_videos.put(f)  # Store file and get its unique ID
        print(f"Stored with ID: {fid}")
    except Exception as err:
        print(f"GridFS error: {err}")  # Log error for debugging
        traceback.print_exc()                # Print stack trace for debugging
        return "internal server error", 500  # Return generic error response

    # Construct message payload for RabbitMQ
    message = {
        "video_fid": str(fid),         # ID of the uploaded video file
        "mp3_fid": None,               # Placeholder for future mp3 file ID
        "username": access["username"] # User who initiated the upload
    }

    # Attempt to publish message to RabbitMQ queue
    try:
        print(f"Publishing to RabbitMQ: {message}")
        channel.basic_publish(
            exchange="",               # Default exchange (direct routing)
            routing_key="video",       # Queue name for video processing
            body=json.dumps(message),  # Serialize message as JSON
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # Make message durable
            ), 
        )
    except Exception as err:
        print(f"RabbitMQ error: {err}")      # Log error
        traceback.print_exc()                # Print stack trace for debugging
        fs_videos.delete(fid)  # Roll back file upload if publish fails
        return "internal server error", 500  # Return error response

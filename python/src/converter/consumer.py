
# Purpose: Listens to a RabbitMQ queue for video conversion tasks, retrieves video files from MongoDB GridFS,
# converts them to MP3 using the convert module, and stores the result back into GridFS.


import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3



def main():
    # Connect to MongoDB running inside Minikube.
    # `host.minikube.internal` resolves to the host machine from inside the container.
    # Port 27017 is MongoDB's default.
    client = MongoClient("host.minikube.internal", 27017)

    # Access two separate databases:
    # - `videos`: stores original video files
    # - `mp3s`: stores converted audio files
    db_videos = client.videos
    db_mp3s = client.mp3s

    # Initialize GridFS handlers for each database.
    # GridFS allows storage of files larger than MongoDB's BSON document limit (16MB).
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # Establish a blocking connection to RabbitMQ.
    # This ensures the consumer stays alive and listens continuously.
    # Assumes RabbitMQ is reachable via service name `rabbitmq` (e.g., Kubernetes DNS).
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Define the callback function that will be triggered when a message is received.
    # `body` is expected to contain metadata or an identifier for the video to convert.
    def callback(ch, method, properties, body):
        # Call the conversion function with:
        # - `body`: message payload (e.g., video ID or filename)
        # - `fs_videos`: GridFS handler for input videos
        # - `fs_mp3s`: GridFS handler for output MP3s
        # - `ch`: RabbitMQ channel, passed in case the conversion function needs to publish or log
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)

        # Acknowledge or reject the message based on conversion success.
        # - `basic_ack`: confirms successful processing
        # - `basic_nack`: signals failure, allowing message to be requeued or logged
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # Start consuming messages from the queue defined in the environment variable `VIDEO_QUEUE`.
    # `on_message_callback` binds the callback function to incoming messages.
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    # Log readiness to the console.
    # This is useful for debugging and confirming that the consumer is live.
    print("Waiting for messages. To exit press CTRL+C")

    # Begin the blocking consumption loop.
    # This keeps the script alive and responsive to incoming RabbitMQ messages.
    channel.start_consuming()

# Entry point for the script.
# This block ensures the consumer starts properly and logs any fatal errors during startup.
if __name__ == "__main__":
    try:
        # Attempt to start the main consumer loop
        main()
    except Exception as e:
        # Catch any unexpected errors (not just KeyboardInterrupt)
        import traceback

        # Log a clear error message to the console
        print(" Converter startup failed:", e)

        # Print the full stack trace for debugging
        traceback.print_exc()

        try:
            # Exit with a non-zero status code to signal failure to Kubernetes
            sys.exit(1)
        except SystemExit:
            # Fallback exit method in case sys.exit() is suppressed
            os._exit(1)


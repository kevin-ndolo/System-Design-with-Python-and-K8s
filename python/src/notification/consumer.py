# Purpose: Listens to RabbitMQ for MP3 conversion completion messages,
# triggers email notifications via the send.email module.

import pika, sys, os, time
from send import email  # Custom module for sending email notifications


def main():
    # Establish a blocking connection to RabbitMQ
    # Ensures the consumer stays alive and listens continuously
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Define the callback function triggered when a message is received
    # The message body is passed to the email.notification() function
    def callback(ch, method, properties, body):
        err = email.notification(body)  # Attempt to send email notification

        # Acknowledge or reject the message based on notification success
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  # Signal failure
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirm success

    # Start consuming messages from the queue defined in the environment variable MP3_QUEUE
    # This binds the callback function to incoming messages
    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback
    )

    # Log readiness to the console
    print("Waiting for messages. To exit press CTRL+C")

    # Begin the blocking consumption loop
    channel.start_consuming()


# Entry point for the script
# This block ensures graceful shutdown on keyboard interrupt
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

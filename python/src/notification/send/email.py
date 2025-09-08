# Purpose: Sends an email notification when an MP3 conversion is complete.
# Triggered by the notification consumer when a message arrives from RabbitMQ.

import smtplib, os, json
from email.message import EmailMessage


def notification(message):
    """
    Sends an email to the user notifying them that their MP3 file is ready.

    Args:
        message (str): JSON string containing metadata, including mp3_fid and username

    Returns:
        None if successful, or error object if sending fails
    """

    try:
        # Parse the incoming message from RabbitMQ
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]              # ID of the converted MP3 file
        sender_address = os.environ.get("GMAIL_ADDRESS")   # Gmail sender address
        sender_password = os.environ.get("GMAIL_PASSWORD") # Gmail sender password
        receiver_address = message["username"]    # Email address of the recipient

        # Construct the email message
        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")  # Email body
        msg["Subject"] = "MP3 Download"                           # Email subject
        msg["From"] = sender_address                              # Sender
        msg["To"] = receiver_address                              # Recipient

        # Connect to Gmail SMTP server and send the message
        session = smtplib.SMTP("smtp.gmail.com", 587)  # Use TLS on port 587
        session.starttls()                             # Upgrade to secure connection
        session.login(sender_address, sender_password) # Authenticate
        session.send_message(msg, sender_address, receiver_address)  # Send email
        session.quit()                                 # Close connection

        print("Mail Sent")  # Log success

    except Exception as err:
        # Catch any errors during email construction or sending
        print(f"Email error: {err}")  # Log the error for debugging
        return err                    # Return error to caller (for basic_nack)

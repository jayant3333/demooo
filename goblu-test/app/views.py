import logging
import json
import requests
from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import process_whatsapp_message, is_valid_whatsapp_message
from .data_store import template_message_sent  # Import the dictionary from the new module

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    from datetime import datetime ,timedelta
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    print("body")

    

    message_details = {
        "id": body.get("id"),
        "created": body.get("created"),
        "whatsapp_message_id": body.get("whatsappMessageId"),
        "conversation_id": body.get("conversationId"),
        "ticket_id": body.get("ticketId"),
        "text": body.get("text"),
        "type": body.get("type"),
        "status_string": body.get("statusString"),
        "wa_id": body.get("waId"),
        "sender_name": body.get("senderName"),
        "timestamp": body.get("timestamp"),
    }
     
    print(message_details["created"])

    timestamp = datetime.strptime(message_details["created"].split('.')[0], "%Y-%m-%dT%H:%M:%S")

    # Get the current time
    current_time = datetime.utcnow() - timedelta(minutes=1)

    # Compare the times
    if timestamp < current_time:
        print("The given timestamp is earlier than the current time.")
        l= ['919460733741', '916352698962']
        if message_details['wa_id'] in l:
            logging.info(f"Message details0: {message_details}")
            process_whatsapp_message(body)

        # Log the extracted details
        logging.info(f"Message details: {message_details}")
        print(jsonify({"status": "error", "message": "Invalid JSON provided"}))
        return jsonify({"status": "error", "message": "Invalid JSON provided"})

    else:

        print("The given timestamp is later than or equal to the current time.")
        response = jsonify({"status": "error", "message": "Invalid JSON provided"})
        response.status_code = 200
        return response
       
# Required webhook verification for WhatsApp
def verify():
    # Parse params from the webhook verification request
    print("hello")
    print(request.json)
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    print(token)
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


'''@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()'''

@webhook_blueprint.route("/webhook", methods=["POST"])
# @signature_required
def webhook_post():
    print("Yes Webhook")
    return handle_message()

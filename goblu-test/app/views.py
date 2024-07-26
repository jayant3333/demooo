import logging
import json
import requests
from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import process_whatsapp_message, is_valid_whatsapp_message
from .data_store import template_message_sent  # Import the dictionary from the new module

webhook_blueprint = Blueprint("webhook", __name__)

def send_template_message(to):
    url = "https://graph.facebook.com/v20.0/368948182969171/messages"
    headers = {
        "Authorization": "Bearer EAAuXEbmPW2sBOzStTSW3sB9HibwuGeJ8sTiJgKb82tC3XZCbxrqDZAppZACGvFk4aS2xfwqiThMUXwjQJWAZCwtbvnYs2fAF3pBgZBDY6xGYyrJMidTpvyxOiLXvXy6eUx03xyTvJQo1VDnupSqOZCbI2tiZAFszhZAcs2ejeaNwLIyym20EmfcI9GwlZBFRQPTJofEZCTZCvXuMgPW8Cbd3HcZD",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "starting_message",
            "language": {
                "code": "en"
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def handle_message():
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
    # logging.info(f"request body: {body}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body)

            # Extract the recipient's phone number
            entry = body.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [{}])[0]
            from_phone_number = messages.get("from")

            if from_phone_number:
                # Check if the template message has already been sent to this user
                if not template_message_sent.get(from_phone_number):
                    # Send the template message to the sender
                    template_response = send_template_message(from_phone_number)
                    logging.info(f"Template message response: {template_response}")
                    # Mark the template message as sent for this user
                    template_message_sent[from_phone_number] = True

            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# Required webhook verification for WhatsApp
def verify():
    # Parse params from the webhook verification request
    print("hello")
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


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()

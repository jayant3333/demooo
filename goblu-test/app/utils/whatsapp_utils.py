import logging
from flask import current_app, jsonify
import json
import linecache
import requests
from datetime import date,datetime

from datetime import datetime
from app.services.openai_service import generate_response
import re
from app.data_store import template_message_sent

conversation_history = {}

import os

def send_wati_message(phone_number, message_text, bearer_token, base_url):
    """
    Sends a message using the WATI API.

    Parameters:
        phone_number (str): The recipient's phone number (including country code).
        message_text (str): The text message to be sent.
        bearer_token (str): The authorization token for the API.
        base_url (str): The base URL for the WATI API.

    Returns:
        dict: The response from the API.
    """
    url = f"{base_url}/api/v1/sendSessionMessage/{phone_number}?messageText={message_text}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return response  # Parse the response as JSON and return it
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Example usage
base_url = "https://live-mt-server.wati.io/113918"
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkMzE3MGYxZS0wMTZjLTRmZTYtYjJhNC1hY2I3ZDUzZWNjOGUiLCJ1bmlxdWVfbmFtZSI6ImluZm9AZ29ibHUtZXYuY29tIiwibmFtZWlkIjoiaW5mb0Bnb2JsdS1ldi5jb20iLCJlbWFpbCI6ImluZm9AZ29ibHUtZXYuY29tIiwiYXV0aF90aW1lIjoiMTEvMTkvMjAyNCAwODowOTozMCIsInRlbmFudF9pZCI6IjExMzkxOCIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.1S2Pbk70howvPLDZ2Lfpu3B4SAAUUdolORxTmlO8cdc"



        

def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    """
    Process incoming WhatsApp message and handle different message types.

    Args:
        body (dict): The incoming webhook payload.

    Returns:
        None
    """
    print("Experiment")
    print(body)

    # Extract common details from the new structure
    wa_id = body.get("waId")
    name = body.get("senderName")
    message_type = body.get("type")

    if message_type == "text":
        # Process text messages
        message_body = body.get("text", "")
        response = generate_response(message_body, wa_id, name, message_type,"text2")

    elif message_type == "location":
        # Process location messages
        location = body.get("text", "")
        message_body = str(location)
        response = generate_response(message_body, wa_id, name, message_type,"location2")

    else:
        # Process button or other types of messages
        button_reply = body.get("buttonReply", {}).get("text", "")
        message_body = button_reply if button_reply else "Unsupported message type"
        response = generate_response(message_body, wa_id, name, message_type,"button2")

    # Maintain conversation history
    if wa_id not in conversation_history:
        conversation_history[wa_id] = []
    conversation_history[wa_id].append({"user": message_body, "model": response})

    # Process the response for WhatsApp formatting
    response = process_text_for_whatsapp(response)


    list_of_wa_ids = ['919460733741', '919079661846', '916352698962','916264553145','918955744758','61419469222']  # Example list

    if wa_id in list_of_wa_ids:
        responseit = send_wati_message(wa_id, response, bearer_token, base_url)
        print(responseit)

    
    


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )
def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

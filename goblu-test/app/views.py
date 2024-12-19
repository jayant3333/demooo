import logging
import json
import requests
import sqlite3
import datetime
from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import process_whatsapp_message, is_valid_whatsapp_message
from .data_store import template_message_sent  # Import the dictionary from the new module

webhook_blueprint = Blueprint("webhook", __name__)

DATABASE = "agentsprocess.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_process (
        wa_id TEXT PRIMARY KEY,
        operator_email TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Store data in SQLite
def store_data(wa_id, operator_email, timestamp):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Insert or replace the record
    cursor.execute("""
    INSERT OR REPLACE INTO agent_process (wa_id, operator_email, timestamp)
    VALUES (?, ?, ?)
    """, (wa_id, operator_email, timestamp))
    conn.commit()
    conn.close()

# Fetch data by wa_id
def fetch_data(wa_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT operator_email, timestamp FROM agent_process WHERE wa_id = ?
    """, (wa_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# Verify function
def verify():
    body = request.get_json()
    print("body1111")
    print(body)
    if not body or "waId" not in body or "operatorEmail" not in body:
        response = jsonify({"status": "error", "message": "Invalid JSON provided"})
        response.status_code = 400
        return response

    wa_id = body.get("waId")
    operator_email = body.get("operatorEmail")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store data in SQLite
    store_data(wa_id, operator_email, timestamp)

    response = jsonify({"status": "success", "message": "Data stored successfully"})
    response.status_code = 200
    return response



def handle_message():
    from datetime import datetime ,timedelta
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
    
    print("57945444")
    fetch_result = fetch_data(message_details['wa_id'])
    if fetch_result is not None:
        email, fetch_time = fetch_result

        # Current time
        current_time = datetime.now()

        # Parse the fetched time into a datetime object
        fetch_datetime = datetime.strptime(fetch_time, '%Y-%m-%d %H:%M:%S')

        # Check if the email is not 'info@goblu-ev.com' and the time difference is less than 30 minutes
        if email != 'info@goblu-ev.com' and (current_time - fetch_datetime) < timedelta(minutes=5):
            response = jsonify({"status": "error", "message": "Invalid JSON provided"})
            response.status_code = 200
            print("Not processing")
            return response
        else:
        # Compare the times
            if  (datetime.utcnow() - timestamp).total_seconds()/60 < 2:
                print("The given timestamp is earlier than the current time.")
                l= ['919460733741', '919079661846', '916352698962','916264553145','918955744758','918619766638','918000160789','919782749737','917014717238','917735944281']
                if message_details['wa_id'] in l:
                    logging.info(f"Message details0: {message_details}")
                    process_whatsapp_message(body)

                # Log the extracted details
                logging.info(f"Message details: {message_details}")
                print(jsonify({"status": "error", "message": "Invalid JSON provided"}))
                return jsonify({"status": "error", "message": "Invalid JSON provided"})

            else:
                print("dsjnfdksjnvdskjz")

                print("The given timestamp is later than or equal to the current time.")
                response = jsonify({"status": "error", "message": "Invalid JSON provided"})
                response.status_code = 200
                return response
            
    else:
        if  (datetime.utcnow() - timestamp).total_seconds()/60 < 2:
                print("The given timestamp is earlier than the current time.")
                l= ['919460733741', '919079661846', '916352698962','916264553145','918955744758','918619766638','918000160789','919782749737','917014717238','917735944281','61419469222']
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



@webhook_blueprint.route("/process", methods=["POST"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
# @signature_required
def webhook_post():
    print("Yes Webhook")
    return handle_message()

init_db()

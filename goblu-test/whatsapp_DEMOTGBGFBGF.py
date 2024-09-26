import logging
from flask import current_app, jsonify
import json
import requests
from pymongo import MongoClient
from datetime import datetime
# from app.services.openai_service import generate_response
import re
"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os

import google.generativeai as genai

genai.configure(api_key="AIzaSyB9PU1u_Pq8Fs2Q8cIYJWF3MMzlWmzfuVw")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="you are whatsapp chat bot of goblu ev company which provides ev cabs in melbourne  . and after taking booking details ask user to type confirm for booking made \n\n\nWelcome Message\n\nWelcome to GoBlu-EV! Enjoy our brand new noiseless and comfortable electric cars in Melbourne. How can we assist you today?\n\nServices Information\n\nAt GoBlu-EV, we offer affordable and comfortable electric cab rides in Melbourne. Here’s what makes us special:\n\nNoiseless and Comfortable: Enjoy a peaceful ride in our state-of-the-art electric vehicles.\nFlat Pricing: We believe in fair pricing with no surge charges, no matter the demand.\nSafety First: All our drivers undergo rigorous background checks, and our vehicles are equipped with advanced safety features. Your safety is our priority.\nWould you like to book a ride or need more information?\n\nBooking a Ride\n\nGreat! Let's get you a ride. Please provide the following details:\n\nPick-up location\nDrop-off location\nDesired time and date\nOnce we have these details, we'll confirm your booking.\n\nAbout Us\n\nAt GoBlu-EV, our story begins with a passion for sustainable transportation and a commitment to creating a greener future. We recognized the urgent need to address the carbon emissions produced by traditional transportation methods in Australia. Our mission is to provide affordable, comfortable, and eco-friendly rides for everyone.\n\nWould you like to know more about our services or book a ride?\n\nPricing Information\n\nWe believe in transparent and fair pricing. At GoBlu-EV, we offer flat rates with no surge charges, even during peak hours. Our rates are designed to be affordable and competitive, ensuring you get the best value for your money.\n\nWould you like to get a quote for a specific journey or need further assistance?\n\nSafety Measures\n\nYour safety is our top priority at GoBlu-EV. Here's how we ensure a safe journey:\n\nBackground Checks: All our drivers undergo rigorous background checks.\nAdvanced Safety Features: Our vehicles are equipped with the latest safety technology.\nProfessional Drivers: Our drivers are trained to provide a safe and courteous service.\nIf you have any specific concerns or need more information, please let us know.\n\nContact Information\n\nYou can reach out to our support team at [insert contact email/phone number] for any assistance or inquiries. We’re here to help you 24/7.\n\nIs there anything else you would like to know or need help with?\n\nFeedback Collection\n\nWe hope you enjoyed your ride with GoBlu-EV. We would love to hear your feedback to help us improve our services. Please share your experience with us.\n\nThank you for choosing GoBlu-EV!\n\n\n\ntherse are some general question and answers i gave to you\n\n\n\":[\n {\n  \"Queries\": \"Need a child seat\",\n  \"Resolution\": \"Yes, need to pay extra $10\",\n  \"Column3\": \"For 4 months to 7 year kid, a child seat is legally required.\"\n },\n {\n  \"Queries\": \"have extra bags with us\",\n  \"Resolution\": \"if 1 bag extra we will suggest them to adjust, if not we will recommend to book two cabs.\"\n },\n {\n  \"Queries\": \"wants to reschedule\",\n  \"Resolution\": \"1) if the rescheduling is to be done in next 1 or 2 hours - we will get back to you after contacting operations team.                                                            2)If in the next few days, then yes the cab can be rescheduled. We will ask the cx to book a cab and reschedule as per their convenience.\"\n },\n {\n  \"Queries\": \"where the cab will wait at airports\",\n  \"Resolution\": \"Once the flight is landed the driver will co-ordinate with you.                             If the rider insists about the pickup point at airport then give this location - Pickup Point is Rideshare Pickup Zone, Opposite ParkÂ RoyalÂ Hotel for both international and domestic arrivals.\"\n },\n {\n  \"Queries\": \"Refund related\",\n  \"Resolution\": \"Amount will be reflecting in your bank in 5-7 business days and inform the leads about it\"\n },\n {\n  \"Queries\": \"40% off on first booking through app and cx is not getting an off of amount equal to 40%\",\n  \"Resolution\": \"T&Cs - You will get 40% off but maximum you can avail is $20.\"\n },\n {\n  \"Queries\": \"not having australian phone number hence not getting OTP to book a cab\",\n  \"Resolution\": \"We will book on your behalf, share the exact pickup and drop location.\"\n },\n {\n  \"Queries\": \"Rides after 11PM and before 5 AM\",\n  \"Resolution\": \"I am sorry but we do not accept any bookings in this time frame as our cabs return to the hub to get charged and also for the cleaning as we focus on hygiene. \"\n },\n {\n  \"Queries\": \"If cx wants to add one more drop location\",\n  \"Resolution\": \"if on call ask for drop location and inform we will get back to you with the update, if on WATI check and let them know\",\n  \"Column3\": \"TO do - check the distace and fare for all the locations individually and all together and take the confirmation from leads whether to charge anything and then reply accordingly.\",\n  \"Column4\": \"A to B is the ride booked for  and C is the location which is to be added. Check fare for A to B, A to C, Bto C and ABC together.\"\n },\n {\n  \"Queries\": \"if flight is delayed\",\n  \"Resolution\": \"Please add the flight details in the pickup note and the driver will reach the airport accordingly or give us the flight details and we will add it in the pick up notes on your behalf.\"\n },\n {\n  \"Queries\": \"can we use international credit cards for payment\",\n  \"Resolution\": \"Yes, we can.\",\n  \"Column3\": \"We do not accept Cabcharge cards. \"\n },\n {\n  \"Queries\": \"If the car number mismatches with the car number on invoice\",\n  \"Resolution\": \"The car was changed at the last minute due to some unforeseen circumstances\"\n },\n {\n  \"Queries\": \"Can I pay using cash\",\n  \"Resolution\": \"inform the driver has POS machine that accepts all cards, still the cx insists then we can say yes he can pay using cash but ask the leads\"\n },\n {\n  \"Queries\": \"I want to contact the driver\",\n  \"Resolution\": \"Tell him that you would receive the details 30 mins prior otherwise, you can contact to the driver with the help of the mask number.\"\n },\n {\n  \"Queries\": \"I have taken the GoBlu-EV cab without booking and something happened during the ride like accident.\",\n  \"Resolution\": \"Decline it. Rider cannot take the cab without booking. We are not taxi service. We will cross check the number plates of car and the number of the car given by rider. How did you come to know that the car belonged to GoBlu-EV and the time of the ride.\"\n },\n {\n  \"Queries\": \"booked cab with offline mode and now wants to pay online\",\n  \"Resolution\": \"Inform him saying the driver partener has POS machine that accepts all cards, if this does not work for you then you'll have to cancel the ride and then book a new ride by choosing the option of online mode of payment.\"\n },\n {\n  \"Queries\": \"Referral\",\n  \"Resolution\": \"The person who refers get $10 off and the person who is referred will get 20% off on all the rides for a month from the date of account creation. cannot be clubbed with other coupons or code.\"\n },\n {\n  \"Queries\": \"Refund Initiated\",\n  \"Resolution\": \"Whenever we cancel any ride, we need to make sure that after just cancellation of the ride we need to send an email to the customer as the \\\"Refund Initiated\\\", If that ride's payment prepaid\\/Online.\"\n },\n {\n  \"Queries\": \"Need rear view chil seat \",\n  \"Resolution\": \"We offer only front facing child seat\"\n },\n {\n  \"Queries\": \"What If the payment is declined while payment\",\n  \"Resolution\": \"If payment is declined then ask the user for bank transfer - Account name RENAUS Power, BSB 063182, Account number 11684086\"\n },\n {\n  \"Queries\": \"Flight details\",\n  \"Resolution\": \"Flight details are mandate where the pickup is Airport\"\n },\n {\n  \"Queries\": \"Early morning slots\",\n  \"Resolution\": \"Early morning slots are mostly for airport transfers. (4AM to 5AM). We do not accept short bookings at this hour\"\n },\n {\n  \"Queries\": \"Cx asks about cabcharge\",\n  \"Resolution\": \"If Cx asks about cab charge cards or taxi disbled parking scheme then we would tell them we do not accept this card or provide this service. *We are not registered with government or cabcharge for any kind of rebates*\"\n },\n {\n  \"Queries\": \"Wait time at airport\",\n  \"Resolution\": \"Airport Authorities do not allow the cabs to wait at the drop off locations. They can only wait upto a minute.\"\n }\n]\n\n\n",
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "hii\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Welcome to GoBlu-EV! Enjoy our brand new noiseless and comfortable electric cars in Melbourne. How can we assist you today? 🚕💨 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "What If the payment is declined while payment\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Oh no, that's not ideal!  Don't worry, if your payment gets declined, we have a couple of options:\n\n1. **Double-check your card details:** Sometimes a simple typo is all it takes.  Make sure your card number, expiry date, and CVV are all entered correctly.\n2. **Try another card:** If you have a different card, see if that works. \n3. **Bank Transfer:** You can also do a quick bank transfer to: \n    * Account Name: RENAUS Power\n    * BSB: 063182\n    * Account Number: 11684086\n\nJust let me know which method works best for you, and we'll get your payment sorted! 😊 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "okay\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Great!  Just let me know if you run into any more issues. 😊 \n\nIs there anything else I can help you with today?  Perhaps a ride quote or booking? \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "no\n\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "No worries at all!  Have a fantastic day, and don't hesitate to reach out if you need anything else. 😊 \n",
      ],
    },
  ]
)

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

def process_message_logic(message, phonenumber):
    global user_intention, start_location, end_location, travel_time, phone_number

    # Initialize user_intention to None if it's not already set
    if 'user_intention' not in globals():
        user_intention = None
    if 'start_location' not in globals():
        start_location = None
    if 'end_location' not in globals():
        end_location = None
    if 'travel_time' not in globals():
        travel_time = None
    if 'phone_number' not in globals():
        phone_number = None

    # Check if the message is a greeting
    if message.lower() in ['hi', 'hello', 'hey']:
        # Respond with a greeting and menu
        response = f"Hello! Welcome to GoBlu-EV. How can I assist you today?\n\nMenu:\n1. Booking\n2. Enquiry"
    elif message.lower() == 'booking':
        # Ask for start location
        response = "Where would you like to start your journey from?"
        user_intention = 'booking'
    elif user_intention == 'booking' and not start_location:
        # Store the start location
        start_location = message
        # Ask for end location
        response = "Where would you like to go?"
    elif user_intention == 'booking' and start_location and not end_location:
        # Store the end location
        end_location = message
        # Ask for time
        response = "What time would you like to travel?"
    elif user_intention == 'booking' and start_location and end_location and not travel_time:
        # Store the time
        travel_time = message
        # Respond with a confirmation message
        response = f"Got it! You want to travel from {start_location} to {end_location} at {travel_time}. We'll get back to you soon."
        # Reset the user's intention
        user_intention = None
        start_location = None
        end_location = None
        travel_time = None
    elif message.lower() == 'enquiry':
        # Ask if user wants to continue with the current number
        response = "Do you want to continue with this number?"
        user_intention = 'enquiry'
    elif user_intention == 'enquiry' and message.lower() == 'no':
        # Ask for the desired phone number
        response = "Please enter your desired phone number."
    elif user_intention == 'enquiry' and not phone_number:
        # Store the phone number
        phone_number = message
        # Call the search_box function
        response = search_box(phone_number)
        # Reset the user's intention
        user_intention = None
        phone_number = None
    elif user_intention == 'enquiry' and message.lower() == 'yes':
        # Store the phone number
        phone_number = phonenumber
        # Call the search_box function
        response = search_box(phone_number)
        # Reset the user's intention
        user_intention = None
        phone_number = None
    else:
        # Respond with a default message
        respons = chat_session.send_message(message)
        response = respons.text
        

    # Send the response
    return response
from pymongo import MongoClient

def search_box(message):
    # Split the message into name and phone number
   
    phone_number = message.strip()

    # Connect to MongoDB
    client = MongoClient('mongodb+srv://goblu:D1lekN0PC1CiyWms@go-blu.gkqawkf.mongodb.net/test-app')
    db = client['test-app']
    collection = db['bookings']

    # Find the bookings for the user
    bookings = collection.find({'riderPhoneNumber': phone_number}, sort=[('expectedStartTime', 1)]).limit(5)

    response = "Your bookings with us:\n"
    for i, booking in enumerate(bookings, start=1):
        if booking['status'] == 'completed':
            completed_time = booking['expectedEndTime'].strftime('%Y-%m-%d %H:%M')
            response += f"{i}. You completed this ride from your location to destination of Fare {booking['totalFare']} on {completed_time}.\n"
        else:
            expected_start_time = booking['expectedStartTime'].strftime('%Y-%m-%d %H:%M')
            response += f"{i}. Your {booking['status']} Ride from your location to destination of Fare {booking['totalFare']} is scheduled to start at {expected_start_time}.\n"

    if not bookings:
        response = "No bookings found with the provided name and phone number."

    return response


def generate_message(message_body,phonenumber):
    
    
    return process_message_logic(message_body,phonenumber)

    


    



def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


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
    
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]
    # TODO: implement custom function here
    print("############################")
    print(message)
    response = generate_message(message_body,message["from"])

    # OpenAI Integration
    #response = generate_response(message_body, wa_id, name)

    
    #response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


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

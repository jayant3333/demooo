import logging
import json
import requests
from datetime import date,datetime
import os
import shelve

from datetime import datetime
# from app.services.openai_service import generate_response
import re
from app.data_store import template_message_sent
import google.generativeai as genai
"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os

import google.generativeai as genai
conversation_history = {}

genai.configure(api_key="AIzaSyCOIM-iwFeaVE6G16sp_e5DetvFlb-JHyk")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 0.9,
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
  system_instruction="you are whatsapp chat bot of goblu ev company which provides ev cabs in melbourne. 2.the current year us 2024 so take year of boking by default as 2024 3.ask user one by one detalis like pickup then drop off then  date time take date as an dd/mm/yyyy format  and plese take care of this ::(take year as 2024 when not specified and time as HH:MM 12 HRS format) for (ex:5:40 PM)  after takeing all these detalis ask user to type 'confirm' only remember this is strictly  needed to tyoe only word confirm and dont show confirm in every prompt after user entered all details then ask to type confirm take locations are in melbourne only including these suburbs Carlton, Docklands, East Melbourne, Flemington, Kensington, North Melbourne, Parkville, Southbank, South Yarra, West Melbourne, Balwyn, Box Hill, Burwood, Camberwell, Doncaster, Glen Iris, Hawthorn, Kew, Mount Waverley, Surrey Hills, Brunswick, Coburg, Essendon, Fawkner, Northcote, Preston, Reservoir, Thornbury, Altona, Braybrook, Footscray, Maribyrnong, Sunshine, Werribee, Williamstown, Bentleigh, Brighton, Cheltenham, Elsternwick, Elwood, Hampton, Mentone, Moorabbin, Sandringham, St Kilda, Clayton, Dandenong, Glen Waverley, Noble Park, Springvale, Beaumaris, Black Rock, Highett, Berwick, Cranbourne, Ferntree Gully, Frankston, Lilydale, Melton, Narre Warren, Pakenham, Ringwood, Sunbury notify user if the location is not in melbourne \n\n\nWelcome Message\n\nWelcome to GoBlu-EV! Enjoy our brand new noiseless and comfortable electric cars in Melbourne. How can we assist you today?\n\nServices Information\n\nAt GoBlu-EV, we offer affordable and comfortable electric cab rides in Melbourne. Here’s what makes us special:\n\nNoiseless and Comfortable: Enjoy a peaceful ride in our state-of-the-art electric vehicles.\nFlat Pricing: We believe in fair pricing with no surge charges, no matter the demand.\nSafety First: All our drivers undergo rigorous background checks, and our vehicles are equipped with advanced safety features. Your safety is our priority.\nWould you like to book a ride or need more information?\n\nBooking a Ride\n\nGreat! Let's get you a ride. Please provide the following details:\n\nPick-up location\nDrop-off location\nDesired time and date\nOnce we have these details, we'll confirm your booking.\n\nAbout Us\n\nAt GoBlu-EV, our story begins with a passion for sustainable transportation and a commitment to creating a greener future. We recognized the urgent need to address the carbon emissions produced by traditional transportation methods in Australia. Our mission is to provide affordable, comfortable, and eco-friendly rides for everyone.\n\nWould you like to know more about our services or book a ride?\n\nPricing Information\n\nWe believe in transparent and fair pricing. At GoBlu-EV, we offer flat rates with no surge charges, even during peak hours. Our rates are designed to be affordable and competitive, ensuring you get the best value for your money.\n\nWould you like to get a quote for a specific journey or need further assistance?\n\nSafety Measures\n\nYour safety is our top priority at GoBlu-EV. Here's how we ensure a safe journey:\n\nBackground Checks: All our drivers undergo rigorous background checks.\nAdvanced Safety Features: Our vehicles are equipped with the latest safety technology.\nProfessional Drivers: Our drivers are trained to provide a safe and courteous service.\nIf you have any specific concerns or need more information, please let us know.\n\nContact Information\n\nYou can reach out to our support team at [insert contact email/phone number] for any assistance or inquiries. We’re here to help you 24/7.\n\nIs there anything else you would like to know or need help with?\n\nFeedback Collection\n\nWe hope you enjoyed your ride with GoBlu-EV. We would love to hear your feedback to help us improve our services. Please share your experience with us.\n\nThank you for choosing GoBlu-EV!\n\n\n\ntherse are some general question and answers i gave to you\n\n\n\":[\n {\n  \"Queries\": \"Need a child seat\",\n  \"Resolution\": \"Yes, need to pay extra $10\",\n  \"Column3\": \"For 4 months to 7 year kid, a child seat is legally required.\"\n },\n {\n  \"Queries\": \"have extra bags with us\",\n  \"Resolution\": \"if 1 bag extra we will suggest them to adjust, if not we will recommend to book two cabs.\"\n },\n {\n  \"Queries\": \"wants to reschedule\",\n  \"Resolution\": \"1) if the rescheduling is to be done in next 1 or 2 hours - we will get back to you after contacting operations team.                                                            2)If in the next few days, then yes the cab can be rescheduled. We will ask the cx to book a cab and reschedule as per their convenience.\"\n },\n {\n  \"Queries\": \"where the cab will wait at airports\",\n  \"Resolution\": \"Once the flight is landed the driver will co-ordinate with you.                             If the rider insists about the pickup point at airport then give this location - Pickup Point is Rideshare Pickup Zone, Opposite ParkÂ RoyalÂ Hotel for both international and domestic arrivals.\"\n },\n {\n  \"Queries\": \"Refund related\",\n  \"Resolution\": \"Amount will be reflecting in your bank in 5-7 business days and inform the leads about it\"\n },\n {\n  \"Queries\": \"40% off on first booking through app and cx is not getting an off of amount equal to 40%\",\n  \"Resolution\": \"T&Cs - You will get 40% off but maximum you can avail is $20.\"\n },\n {\n  \"Queries\": \"not having australian phone number hence not getting OTP to book a cab\",\n  \"Resolution\": \"We will book on your behalf, share the exact pickup and drop location.\"\n },\n {\n  \"Queries\": \"Rides after 11PM and before 5 AM\",\n  \"Resolution\": \"I am sorry but we do not accept any bookings in this time frame as our cabs return to the hub to get charged and also for the cleaning as we focus on hygiene. \"\n },\n {\n  \"Queries\": \"If cx wants to add one more drop location\",\n  \"Resolution\": \"if on call ask for drop location and inform we will get back to you with the update, if on WATI check and let them know\",\n  \"Column3\": \"TO do - check the distace and fare for all the locations individually and all together and take the confirmation from leads whether to charge anything and then reply accordingly.\",\n  \"Column4\": \"A to B is the ride booked for  and C is the location which is to be added. Check fare for A to B, A to C, Bto C and ABC together.\"\n },\n {\n  \"Queries\": \"if flight is delayed\",\n  \"Resolution\": \"Please add the flight details in the pickup note and the driver will reach the airport accordingly or give us the flight details and we will add it in the pick up notes on your behalf.\"\n },\n {\n  \"Queries\": \"can we use international credit cards for payment\",\n  \"Resolution\": \"Yes, we can.\",\n  \"Column3\": \"We do not accept Cabcharge cards. \"\n },\n {\n  \"Queries\": \"If the car number mismatches with the car number on invoice\",\n  \"Resolution\": \"The car was changed at the last minute due to some unforeseen circumstances\"\n },\n {\n  \"Queries\": \"Can I pay using cash\",\n  \"Resolution\": \"inform the driver has POS machine that accepts all cards, still the cx insists then we can say yes he can pay using cash but ask the leads\"\n },\n {\n  \"Queries\": \"I want to contact the driver\",\n  \"Resolution\": \"Tell him that you would receive the details 30 mins prior otherwise, you can contact to the driver with the help of the mask number.\"\n },\n {\n  \"Queries\": \"I have taken the GoBlu-EV cab without booking and something happened during the ride like accident.\",\n  \"Resolution\": \"Decline it. Rider cannot take the cab without booking. We are not taxi service. We will cross check the number plates of car and the number of the car given by rider. How did you come to know that the car belonged to GoBlu-EV and the time of the ride.\"\n },\n {\n  \"Queries\": \"booked cab with offline mode and now wants to pay online\",\n  \"Resolution\": \"Inform him saying the driver partener has POS machine that accepts all cards, if this does not work for you then you'll have to cancel the ride and then book a new ride by choosing the option of online mode of payment.\"\n },\n {\n  \"Queries\": \"Referral\",\n  \"Resolution\": \"The person who refers get $10 off and the person who is referred will get 20% off on all the rides for a month from the date of account creation. cannot be clubbed with other coupons or code.\"\n },\n {\n  \"Queries\": \"Refund Initiated\",\n  \"Resolution\": \"Whenever we cancel any ride, we need to make sure that after just cancellation of the ride we need to send an email to the customer as the \\\"Refund Initiated\\\", If that ride's payment prepaid\\/Online.\"\n },\n {\n  \"Queries\": \"Need rear view chil seat \",\n  \"Resolution\": \"We offer only front facing child seat\"\n },\n {\n  \"Queries\": \"What If the payment is declined while payment\",\n  \"Resolution\": \"If payment is declined then ask the user for bank transfer - Account name RENAUS Power, BSB 063182, Account number 11684086\"\n },\n {\n  \"Queries\": \"Flight details\",\n  \"Resolution\": \"Flight details are mandate where the pickup is Airport\"\n },\n {\n  \"Queries\": \"Early morning slots\",\n  \"Resolution\": \"Early morning slots are mostly for airport transfers. (4AM to 5AM). We do not accept short bookings at this hour\"\n },\n {\n  \"Queries\": \"Cx asks about cabcharge\",\n  \"Resolution\": \"If Cx asks about cab charge cards or taxi disbled parking scheme then we would tell them we do not accept this card or provide this service. *We are not registered with government or cabcharge for any kind of rebates*\"\n },\n {\n  \"Queries\": \"Wait time at airport\",\n  \"Resolution\": \"Airport Authorities do not allow the cabs to wait at the drop off locations. They can only wait upto a minute.\"\n }\n]\n\n\n",
)


def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

# Store a thread
def store_thread(wa_id, history):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = history



current_state = None

def generate_response(message_body, wa_id, name):
    global current_state
    
    # Check if there is already a conversation history for the wa_id
    history = check_if_thread_exists(wa_id)

    # If no history exists, initialize a new conversation
    if history is None :
        history = []

    # Add the new user message to the history
    history.append({
        "role": "user",
        "parts": [message_body]
    })

    # Start or continue the chat session
    chat_session = model.start_chat(history=history)

    if len(history) > 2:
        j = chat_session.history[-2].role
        y = chat_session.history[-2].parts
        y = str(y)
        desired_string = y.strip('[text: "').strip('" ]')
        if j == "model" and "confirm" in desired_string and current_state == "booking":
            current_state = "confirm"

    # Get the model's response
    
    list = ["hello","hii","HI","HELLO","hi","Hello"]
    # Extract conversation state from message_body
    message_body_lower = message_body.lower()
    if message_body_lower in list:
        send_template_message(wa_id)
        return ""
    if "enquiry" in message_body_lower:
        current_state = "enquiry"
    elif "booking" in message_body_lower:
        current_state = "booking"
    elif "complaints and feedback" in message_body_lower:
        current_state = "complaints and feedback"
    elif "confirm" in message_body_lower:

        current_state = "confirm"
    
    # Handle conversation states
    if current_state == "enquiry":
        response = chat_session.send_message(message_body)
        history.append({
            "role": "model",
            "parts": [response.text]
        })
        store_thread(wa_id, history)
        return response.text
    elif current_state == "booking":
        while current_state == "booking":
            # Generate response from agent
            agent_response = chat_session.send_message(message_body)
            history.append({
                "role": "model",
                "parts": [agent_response.text]
            })
            store_thread(wa_id, history)
            return agent_response.text
    elif current_state == "complaints and feedback":
        response = chat_session.send_message(message_body)
        history.append({
            "role": "model",
            "parts": [response.text]
        })
        store_thread(wa_id, history)
        return response.text
    elif current_state == "confirm":
        # Handle confirmation
        datai = chat_session.send_message("give me all booking details in python dict as the date as DD/MM/YYYY and time as HH:MM 12 hrs format no extra text only dict as keys as up,down,time,date")

        text = datai.text
        keys = ["up", "down", "time", "date"]
        values = []

        for key in keys:
            pattern = r"'" + key + r"':\s*'([^']*)'"
            match = re.search(pattern, text)
            if match:
                values.append(match.group(1))

        # Check availability in API
        api_response_drop = check_availability_in_api_drop(values[1])
        api_response_pick = check_availability_in_api_pick(values[0])
        fare = get_ride_fare(values[0], values[1])
        Fare = fare['fare']
        global api_data 
        api_data = []
        api_data.append(values[0])
        api_data.append(values[1])
        time = convert_time_date(values[2], values[3])
        ty = get_time_slot_availability(values[0], values[1], time)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(time)
        print(api_response_drop)
        print(api_response_pick)
        print(ty['availability'])
        iso = convert_to_iso8601(time)
        api_data.append(iso)
        api_data.append(ty)
        if api_response_drop and api_response_pick and ty['availability']:
            current_state = "confirm_yes_no"
            response_text = f"We are servicing here and slot is also available, the fare is {Fare}.{send_template_message_yes(wa_id)}"
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history)
            return response_text
        else:
            current_state = "booking"
            chat_session.send_message("confirm")
            return "we are not servicing here or slot is not available"

    elif current_state == "confirm_yes_no":
        if message_body_lower == "yes":
            current_state = "enquiry"
            res = book_cab(api_data[0],api_data[1],api_data[2],name,wa_id,api_data[3]['vehicle']['id'])
            print(type(api_data[3]['vehicle']['id']))
            print(type(name))
            print(type(wa_id))
            print(type(api_data[0]))
            print(type(api_data[1]))
            print(type(api_data[2]))
            api_data = []
            print("########################")
            print(res)
            response_text = "Congratulations! Your eco-friendly ride with GoBlu-EV has been confirmed. Driver details will be shared 30 mins before the ride starts. Check our app for the ride details. For any assistance call +97148718604 or mail support@noorride.com. Have a safe ride."
            chat_session.send_message("confirm")
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history)
            return response_text
        elif message_body_lower == "no":
            api_data = []
            current_state = "enquiry"
            response_text = "Booking cancelled!"
            chat_session.send_message("booking cancelled")
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history)
            return response_text
        else:
            current_state = "confirm_yes_no"
            response_text = f"Invalid response. Please respond with 'yes' or 'no'.{send_template_message_yes(wa_id)}"
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history)
            return response_text


import requests

def book_cab(pickup_loc, drop_loc, date_time, name, phone_number, booking_id):
    # Define the API endpoint
    url = "https://webapi.goblu-ev.com/v1/call/cab_booking/"

    # Define the parameters
    params = {
        "pickup_loc": pickup_loc,
        "drop_loc": drop_loc,
        "date_time": date_time,
        "name": name,
        "phoneNumber": phone_number,
        "id": booking_id
    }

    try:
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Check if the response is JSON
        try:
            response_data = response.json()
        except ValueError:
            return response.status_code, {"success": False, "message": "Response is not JSON"}
        
        return response.status_code, response_data
    
    except requests.exceptions.RequestException as e:
        return None, {"success": False, "message": str(e)}


def convert_to_iso8601(date_time_str):
    # Assume the year 2024 and append it to the input date string
    date_time_str = f"2024-{date_time_str}"
    
    # Parse the string into a datetime object
    dt = datetime.strptime(date_time_str, "%Y-%d-%m %H:%M")
    
    # Convert to ISO 8601 format
    iso8601_format = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Truncate the microseconds to milliseconds
    return iso8601_format[:-3] + 'Z'

def send_template_message(to):
    url = "https://graph.facebook.com/v20.0/368948182969171/messages"
    headers = {
        "Authorization": "Bearer EAAuXEbmPW2sBOZBLfFHJKCPAEVcfg2iHmqxkoxBZBLyhx48DXlDmrMEakZCNfhZBcVzBlPQZA8aUkyse0wKqSVyXC3eyDfLg9rTM4oSLnUHbPmjhZAZA8q3aB4ue3rHfmYrnZCHzQqwZAVKTCLlmJ5oXkySlxaZB6ksZBiU5wm2P9JB7yp519Ah5v4mLEpi2btcZB0ks065dZBKnZBGouI1ZCcp0w2BL5fSFbnVWHV4aHZBAMDT2",
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
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://media-cdn.tripadvisor.com/media/attractions-splice-spp-720x480/12/42/cb/8c.jpg"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": []
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    


def send_template_message_yes(to):
    url = "https://graph.facebook.com/v20.0/368948182969171/messages"
    headers = {
        "Authorization": "Bearer EAAuXEbmPW2sBOZBLfFHJKCPAEVcfg2iHmqxkoxBZBLyhx48DXlDmrMEakZCNfhZBcVzBlPQZA8aUkyse0wKqSVyXC3eyDfLg9rTM4oSLnUHbPmjhZAZA8q3aB4ue3rHfmYrnZCHzQqwZAVKTCLlmJ5oXkySlxaZB6ksZBiU5wm2P9JB7yp519Ah5v4mLEpi2btcZB0ks065dZBKnZBGouI1ZCcp0w2BL5fSFbnVWHV4aHZBAMDT2",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "yes_no",
            "language": {
                "code": "en"
            }
        }
    }
    requests.post(url, headers=headers, data=json.dumps(payload))
    return ""
    
def convert_time_date(time_str, date_str):
    """
    Convert time and date to the desired format.

    Args:
        time_str (str): Time in the format "HH:MM AM/PM".
        date_str (str): Date in the format "DD/MM/YYYY".

    Returns:
        str: Time and date in the format "MM-DD HH:MM".
    """
    # Parse the time and date strings
    time_obj = datetime.strptime(time_str, "%I:%M %p")
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")

    # Combine the time and date objects
    datetime_obj = datetime.combine(date_obj.date(), time_obj.time())

    # Format the datetime object to the desired format
    formatted_str = datetime_obj.strftime("%d-%m %H:%M")

    return formatted_str
def get_ride_fare(pickup_loc, drop_loc):
    """
    Get the ride fare from the GoBlu EV API.

    Args:
        pickup_loc (str): The pickup location.
        drop_loc (str): The drop-off location.

    Returns:
        dict: The fare information from the API response.
    """
    url = "https://webapi.goblu-ev.com/v1/call/get_ride_fare"
    params = {
        "pickup_loc": pickup_loc,
        "drop_loc": drop_loc
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def check_availability_in_api_drop(address):
    """
    Retrieves geocoded latitude and longitude for a given address.

    Args:
        address (str): The address to geocode.

    Returns:
        dict: The geocoded latitude and longitude data if successful, otherwise None.
    """
    url = f"http://anltcs.goblue-ev.com/geocodedLatLong?address={address}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def check_availability_in_api_pick(address):
    """
    Retrieves geocoded latitude and longitude for a given address.

    Args:
        address (str): The address to geocode.

    Returns:
        dict: The geocoded latitude and longitude data if successful, otherwise None.
    """
    url = f"http://anltcs.goblue-ev.com/geocodedLatLong?address={address}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
def tell_agent_to_confirm_booking():
    # Implement API call to tell agent to confirm booking
    # Return response from agent
    pass

def get_time_slot_availability(pickup_loc, drop_loc, date_time):
    """
    Get time slot availability from GoBlu EV API.

    Args:
        pickup_loc (str): Pickup location.
        drop_loc (str): Drop location.
        date_time (str): Date and time in the format "DD-MM HH:MM".

    Returns:
        dict: API response.
    """
    url = "https://webapi.goblu-ev.com/v1/call/time_slot_availability"
    params = {
        "pickup_loc": pickup_loc,
        "drop_loc": drop_loc,
        "date_time": date_time
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

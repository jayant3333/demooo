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
import ast
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
  system_instruction="""You are a WhatsApp chatbot for GoBlu EV, which provides affordable, noiseless EV cabs. The current year is 2024 by default. Your task is to book a cab by collecting the following details from the user:
                        we only take Whatsapp pin as location and google maps link for booking when user providing an address ask him to pin via whatsapp or send google/apple links
                        Pickup Location:
                        Ask the user to share their current location on WhatsApp or provide a Google?Apple Maps or  link.
                        Drop-off Location:
                        Request the user to share a Google/Apple Maps link or pin the drop-off location via WhatsApp.
                        Date and Time:
                        Ask for the date in DD/MM/YYYY format (default year: 2024) and the time in 12-hour format (e.g., 5:40 PM).
                        Confirmation:
                        After collecting all details, show the summary of the booking (pickup location, drop-off location, date, and time).
                        Ask the user to type 'confirm' to finalize the booking. Ensure that only the word 'confirm' is accepted to proceed.
                        Make sure your messages are interactive and include sufficient emojis to make the conversation engaging.
                        



 
                        
                        In Enquiry after 2 querries ask user to type support for contact us 
                        and not ask user for booking when Enquiry
                        About Us\n\nAt GoBlu-EV, our story begins with a passion for sustainable transportation and a commitment to creating a greener future. We recognized the urgent need to address the carbon emissions produced by traditional transportation methods in Australia. Our mission is to provide affordable, comfortable, and eco-friendly rides for everyone.\n\nWould you like to know more about our services or book a ride?\n\nPricing Information\n\nWe believe in transparent and fair pricing. At GoBlu-EV, we offer flat rates with no surge charges, even during peak hours. Our rates are designed to be affordable and competitive, ensuring you get the best value for your money.\n\nWould you like to get a quote for a specific journey or need further assistance?\n\nSafety Measures\n\nYour safety is our top priority at GoBlu-EV. Here's how we ensure a safe journey:\n\nBackground Checks: All our drivers undergo rigorous background checks.\nAdvanced Safety Features: Our vehicles are equipped with the latest safety technology.\nProfessional Drivers: Our drivers are trained to provide a safe and courteous service.\nIf you have any specific concerns or need more information, please let us know.\n\nContact Information\n\nYou can reach out to our support team at [insert contact email/phone number] for any assistance or inquiries. We’re here to help you 24/7.\n\nIs there anything else you would like to know or need help with?\n\nFeedback Collection\n\nWe hope you enjoyed your ride with GoBlu-EV. We would love to hear your feedback to help us improve our services. Please share your experience with us.\n\nThank you for choosing GoBlu-EV!\n\n\n\ntherse are some general question and answers i gave to you\n\n\n\":[\n {\n  \"Queries\": \"Need a child seat\",\n  \"Resolution\": \"Yes, need to pay extra $10\",\n  \"Column3\": \"For 4 months to 7 year kid, a child seat is legally required.\"\n },\n {\n  \"Queries\": \"have extra bags with us\",\n  \"Resolution\": \"if 1 bag extra we will suggest them to adjust, if not we will recommend to book two cabs.\"\n },\n {\n  \"Queries\": \"wants to reschedule\",\n  \"Resolution\": \"1) if the rescheduling is to be done in next 1 or 2 hours - we will get back to you after contacting operations team.                                                            2)If in the next few days, then yes the cab can be rescheduled. We will ask the cx to book a cab and reschedule as per their convenience.\"\n },\n {\n  \"Queries\": \"where the cab will wait at airports\",\n  \"Resolution\": \"Once the flight is landed the driver will co-ordinate with you.                             If the rider insists about the pickup point at airport then give this location - Pickup Point is Rideshare Pickup Zone, Opposite ParkÂ RoyalÂ Hotel for both international and domestic arrivals.\"\n },\n {\n  \"Queries\": \"Refund related\",\n  \"Resolution\": \"Amount will be reflecting in your bank in 5-7 business days and inform the leads about it\"\n },\n {\n  \"Queries\": \"40% off on first booking through app and cx is not getting an off of amount equal to 40%\",\n  \"Resolution\": \"T&Cs - You will get 40% off but maximum you can avail is $20.\"\n },\n {\n  \"Queries\": \"not having australian phone number hence not getting OTP to book a cab\",\n  \"Resolution\": \"We will book on your behalf, share the exact pickup and drop location.\"\n },\n {\n  \"Queries\": \"Rides after 11PM and before 5 AM\",\n  \"Resolution\": \"I am sorry but we do not accept any bookings in this time frame as our cabs return to the hub to get charged and also for the cleaning as we focus on hygiene. \"\n },\n {\n  \"Queries\": \"If cx wants to add one more drop location\",\n  \"Resolution\": \"if on call ask for drop location and inform we will get back to you with the update, if on WATI check and let them know\",\n  \"Column3\": \"TO do - check the distace and fare for all the locations individually and all together and take the confirmation from leads whether to charge anything and then reply accordingly.\",\n  \"Column4\": \"A to B is the ride booked for  and C is the location which is to be added. Check fare for A to B, A to C, Bto C and ABC together.\"\n },\n {\n  \"Queries\": \"if flight is delayed\",\n  \"Resolution\": \"Please add the flight details in the pickup note and the driver will reach the airport accordingly or give us the flight details and we will add it in the pick up notes on your behalf.\"\n },\n {\n  \"Queries\": \"can we use international credit cards for payment\",\n  \"Resolution\": \"Yes, we can.\",\n  \"Column3\": \"We do not accept Cabcharge cards. \"\n },\n {\n  \"Queries\": \"If the car number mismatches with the car number on invoice\",\n  \"Resolution\": \"The car was changed at the last minute due to some unforeseen circumstances\"\n },\n {\n  \"Queries\": \"Can I pay using cash\",\n  \"Resolution\": \"inform the driver has POS machine that accepts all cards, still the cx insists then we can say yes he can pay using cash but ask the leads\"\n },\n {\n  \"Queries\": \"I want to contact the driver\",\n  \"Resolution\": \"Tell him that you would receive the details 30 mins prior otherwise, you can contact to the driver with the help of the mask number.\"\n },\n {\n  \"Queries\": \"I have taken the GoBlu-EV cab without booking and something happened during the ride like accident.\",\n  \"Resolution\": \"Decline it. Rider cannot take the cab without booking. We are not taxi service. We will cross check the number plates of car and the number of the car given by rider. How did you come to know that the car belonged to GoBlu-EV and the time of the ride.\"\n },\n {\n  \"Queries\": \"booked cab with offline mode and now wants to pay online\",\n  \"Resolution\": \"Inform him saying the driver partener has POS machine that accepts all cards, if this does not work for you then you'll have to cancel the ride and then book a new ride by choosing the option of online mode of payment.\"\n },\n {\n  \"Queries\": \"Referral\",\n  \"Resolution\": \"The person who refers get $10 off and the person who is referred will get 20% off on all the rides for a month from the date of account creation. cannot be clubbed with other coupons or code.\"\n },\n {\n  \"Queries\": \"Refund Initiated\",\n  \"Resolution\": \"Whenever we cancel any ride, we need to make sure that after just cancellation of the ride we need to send an email to the customer as the \\\"Refund Initiated\\\", If that ride's payment prepaid\\/Online.\"\n },\n {\n  \"Queries\": \"Need rear view chil seat \",\n  \"Resolution\": \"We offer only front facing child seat\"\n },\n {\n  \"Queries\": \"What If the payment is declined while payment\",\n  \"Resolution\": \"If payment is declined then ask the user for bank transfer - Account name RENAUS Power, BSB 063182, Account number 11684086\"\n },\n {\n  \"Queries\": \"Flight details\",\n  \"Resolution\": \"Flight details are mandate where the pickup is Airport\"\n },\n {\n  \"Queries\": \"Early morning slots\",\n  \"Resolution\": \"Early morning slots are mostly for airport transfers. (4AM to 5AM). We do not accept short bookings at this hour\"\n },\n {\n  \"Queries\": \"Cx asks about cabcharge\",\n  \"Resolution\": \"If Cx asks about cab charge cards or taxi disbled parking scheme then we would tell them we do not accept this card or provide this service. *We are not registered with government or cabcharge for any kind of rebates*\"\n },\n {\n  \"Queries\": \"Wait time at airport\",\n  \"Resolution\": \"Airport Authorities do not allow the cabs to wait at the drop off locations. They can only wait upto a minute.\"\n }\n]"""


)


import sqlite3
from datetime import datetime, timedelta

# Get a connection to the SQLite database
def get_connection():
    return sqlite3.connect("threads_db.sqlite")

# Ensure the database and table exist
def setup_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                wa_id TEXT PRIMARY KEY,
                history TEXT,
                current_state TEXT,
                timestamp DATETIME
            )
        """)
        conn.commit()

# Call setup_database() at the start of your application
setup_database()


import json
from datetime import datetime

def store_thread(wa_id, history, current_state):
    print("Storing thread...")
    current_time = datetime.now().isoformat()  # Store timestamp as ISO format string

    # Serialize the `history` list to a JSON string
    history_json = json.dumps(history)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO threads (wa_id, history, current_state, timestamp)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(wa_id) DO UPDATE SET
                history = excluded.history,
                current_state = excluded.current_state,
                timestamp = excluded.timestamp
        """, (wa_id, history_json, current_state, current_time))
        conn.commit()
        print(f"Thread for wa_id '{wa_id}' stored successfully.")



def check_if_thread_exists(wa_id):
    print("Checking thread...")
    current_time = datetime.now()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT history, current_state, timestamp FROM threads WHERE wa_id = ?", (wa_id,))
        row = cursor.fetchone()

        if row:
            history_json, current_state, thread_timestamp = row
            thread_timestamp = datetime.fromisoformat(thread_timestamp)

            # Deserialize `history` JSON string to a Python list
            history = json.loads(history_json)

            if current_time - thread_timestamp > timedelta(minutes=5):
                print(f"Thread for wa_id {wa_id} is older than 5 minutes. Deleting...")
                delete_thread_history(wa_id)
                return None, None
            else:
                print(f"Thread for wa_id {wa_id} is within 5 minutes. Returning history and state.")
                return history, current_state

        print(f"No thread found for wa_id {wa_id}.")
        return None, None

def delete_thread_history(wa_id):
    print("Deleting thread...")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM threads WHERE wa_id = ?", (wa_id,))
        conn.commit()
        print(f"Thread for wa_id '{wa_id}' deleted successfully.")



def extract_place_info(url):
    # Define regex patterns to extract possible place-related information
    place_name_pattern = re.compile(r'place/([^/?]+)')
    place_id_pattern = re.compile(r's0x[\w\d]+:\w+')

    # Extract place name
    place_name_match = place_name_pattern.search(url)
    place_name = place_name_match.group(1).replace('+', ' ') if place_name_match else 'Place name not found'
    
    # Extract place ID
    place_id_match = place_id_pattern.search(url)
    place_id = place_id_match.group() if place_id_match else 'Place ID not found'

    return place_name, place_id

def get_coordinates(address, api_key):
    # Define the base URL and parameters
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    # Make the GET request to the Geocoding API
    response = requests.get(base_url, params=params)
    
    # Parse the JSON response
    data = response.json()
    
    # Check if the request was successful
    if data['status'] == 'OK':
        # Extract latitude and longitude
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise Exception("Geocoding API error: " + data['status'])
    
def extract_name_and_coordinates_apple(full_string):
    # Regex patterns
    url_pattern = r'https:\/\/maps\.apple\.com\/\?[^ ]+'  # Pattern to extract URL
    name_pattern = r'q=([^&]+)'                          # Pattern to extract name from the URL
    coordinates_pattern = r'll=(-?\d+\.\d+),(-?\d+\.\d+)' # Pattern to extract coordinates

    # Extract URL from the string
    url_match = re.search(url_pattern, full_string)
    url = url_match.group(0) if url_match else None
    
    if url:
        # Extract name
        name_match = re.search(name_pattern, url)
        name = name_match.group(1).replace('%20', ' ') if name_match else None

        # Extract coordinates
        coordinates_match = re.search(coordinates_pattern, url)
        coordinates = coordinates_match.groups() if coordinates_match else (None, None)

        return name, coordinates
    else:
        return None, (None, None)

def extract_coordinates_from_url(url, api_key):
    place_name, _ = extract_place_info(url)
    if place_name == 'Place name not found':
        raise Exception("Place name could not be extracted from the URL")
    
    try:
        lat, lng = get_coordinates(place_name, api_key)
        j  = []
        j.append({"latitude": lat, "longitude": lng})
        j.append(place_name)
        return j
    except Exception as e:
        raise Exception(f"Error retrieving coordinates: {e}")

'''def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)
    
def delete_thread_history(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        if wa_id in threads_shelf:
            del threads_shelf[wa_id]
            print(f"History for wa_id '{wa_id}' deleted successfully.")
        else:
            print(f"No history found for wa_id '{wa_id}'.")

# Store a thread

def store_thread(wa_id, history):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = history
'''

current_state = None
def get_redirect_url(url):
    try:
        response = requests.get(url,allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print(f"An error ocuured: {e}")
        return None
    

def check_serviceable(long,lat):
    url = f"https://devadmin.goblu-ev.com/check_servicable?lat={lat}&long={long}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True  # Assuming the API returns JSON
        else:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": str(e)}
    

def estimate_fare(data):
    url = 'https://webapi.goblu-ev.com/v1/call/estimate-fare'
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()

        # Check if 'packages' exist, if not, return status
        if 'packages' in response_data and response_data['packages']:
            total_fare = response_data['packages'][0].get('totalFare')
            request_id = response_data.get('id')
            return {'totalFare': total_fare, 'id': request_id}
        else:
            # If packages are not present, return status
            status = response_data.get('status')
            message = response_data.get('message')
            return {'status': status, 'message': message}
    else:
        return f"Error: {response.status_code}, {response.text}"
    


def book_ride(request_id):
    url = 'https://webapi.goblu-ev.com/v1/call/schedule-ride'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "requestId": request_id
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON response
    else:
        return f"Error: {response.status_code}, {response.text}"
def push_booking(wa_id, booking_id):
    print("hiii")
    # Load the existing JSON data
    try:
        with open('booking_info.json', 'r') as json_file:
            data = json.load(json_file)
            print("file open")
    except FileNotFoundError:
        # Initialize an empty dictionary if the file doesn't exist
        data = {}

    # If wa_id exists, append the new booking_id to the list (stack)
    if wa_id in data:
        data[wa_id].append(booking_id)
        print("hgjyg")
    else:
        # Create a new list for the wa_id if it doesn't exist
        print("ggdfgdfg")
        data[wa_id] = [booking_id]

    # Save updated data back to the JSON file
    with open('booking_info.json', 'w') as json_file:
        print("gfdsgtgdfgghfhgfhgfhfh")
        json.dump(data, json_file)
def get_most_recent_booking_id(wa_id):
    # Load the JSON file
    try:
        with open('booking_info.json', 'r') as json_file:
            data = json.load(json_file)
            print(data)
    except FileNotFoundError:
        # Return None if the file or wa_id doesn't exist
        return None

    # Return the most recent booking (last in the list)
    if wa_id in data and data[wa_id]:
        print(data[wa_id])
        return data[wa_id][-1]  # Peek the top of the stack
    else:
        return None  # Return None if wa_id not found or list is empty

def generate_response(message_body, wa_id, name,message_type,prev):
    print(prev)
    global current_state
    print(message_type)
    print(message_body)
    print(type(message_body))
    print(current_state)
    print(current_state)
    list = ["hello","hii","HI","HELLO","hi","Hello","Hi","Hii"]
    # Extract conversation state from message_body
    message_body_lower = message_body.lower()
    if message_body_lower in list:
        delete_thread_history(wa_id)
        send_wati_sms_greet(wa_id)
        return ""
    # Check if there is already a conversation history for the wa_id
    history , current_state = check_if_thread_exists(wa_id)
    
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

    '''if len(history) > 2:
        j = chat_session.history[-2].role
        y = chat_session.history[-2].parts
        y = str(y)
        desired_string = y.strip('[text: "').strip('" ]')
        if j == "model" and "confirm" in desired_string and current_state == "booking":
            current_state = "confirm"'''

    # Get the model's response

    if "enquiry" in message_body_lower:
        current_state = "enquiry"
    elif "booking" in message_body_lower:
        current_state = "booking"
    elif "complains and feedbacks" in message_body_lower:
        current_state = "complaints and feedback"
    elif "confirm" in message_body_lower:
        current_state = "confirm"
    if current_state == None:
        send_wati_sms_greet(wa_id)
        return ""
        
    # Handle conversation states
    if current_state == "enquiry":
        response = chat_session.send_message(message_body)
        history.append({
            "role": "model",
            "parts": [response.text]
        })
        store_thread(wa_id, history,current_state)
        return response.text
    elif current_state == "booking":
        while current_state == "booking":
            # Generate response from agent
            if(message_type == "location"):
                print("hiiiiiiiiiiiiiii")
                print(message_body)
                
                match = re.search(r"https://www\.google\.com/maps/search/([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)", message_body)

                if match:
                    latitude = float(match.group(1))
                    longitude = float(match.group(2))
                    location_list = [latitude, longitude]
                    print(location_list)
                else:
                    print("Invalid message body format")
        
                rer = check_serviceable(location_list[0],location_list[1])
                if rer == False:
                    return """ Oops! We're not servicing your location right now. 😔 But don’t worry! You can check our serviceable areas here: 🌍 at https://goblu-ev.com/service. We hope to serve you soon! 🚗💨 If you have any other questions, feel free to ask! 😊.   To Start Over Just type *Booking* """
                else:
                    agent_response = chat_session.send_message(str(location_list))
                    history.append({
                        "role": "model",
                        "parts": [agent_response.text]
                    })
                    store_thread(wa_id, history,current_state)
                    return agent_response.text
            

            if message_type == "text" and "maps.app.goo.gl" in message_body :
                url = get_redirect_url(message_body)
                api_key = 'AIzaSyCK-SFNb7CADDqinlFmffTuRGBWwEt0J7A'
                coordinates = extract_coordinates_from_url(url, api_key)
                lat = coordinates[0]['latitude']
                long = coordinates[0]['longitude']
                res = check_serviceable(lat,long)

                if(res == False):
                    return " Oops! We're not servicing your location right now. 😔 But don’t worry! You can check our serviceable areas here: 🌍 at https://goblu-ev.com/service. We hope to serve you soon! 🚗💨 If you have any other questions, feel free to ask! 😊.  To Start Over Just type *Booking*"
                else:
                    m = str(coordinates)
                    m = m + coordinates[1]
                    agent_response = chat_session.send_message(m)
                    history.append({
                        "role": "model",
                        "parts": [agent_response.text]
                    })
                    store_thread(wa_id, history,current_state)
                    return agent_response.text
                
            elif  message_type == "text" and "maps.apple.com" in message_body:
                nam , coordinates = extract_name_and_coordinates_apple(message_body)
                lat = coordinates[0]
                long = coordinates[1]
                res = check_serviceable(lat,long)
                if(res == False):
                    return " Oops! We're not servicing your location right now. 😔 But don’t worry! You can check our serviceable areas here: 🌍 at https://goblu-ev.com/service. We hope to serve you soon! 🚗💨 If you have any other questions, feel free to ask! 😊.  To Start Over Just type *Booking*"
                else:
                    m = str(coordinates)
                    m = m + nam
                    agent_response = chat_session.send_message(m)
                    history.append({
                        "role": "model",
                        "parts": [agent_response.text]
                    })
                    store_thread(wa_id, history,current_state)
                    return agent_response.text

            else:
                
                agent_response = chat_session.send_message(message_body)
                history.append({
                    "role": "model",
                    "parts": [agent_response.text]
                })
                store_thread(wa_id, history,current_state)
                return agent_response.text
    elif current_state == "complaints and feedback":
        response = chat_session.send_message(message_body)
        history.append({
            "role": "model",
            "parts": [response.text]
        })
        store_thread(wa_id, history,current_state)
        return response.text
    
    elif current_state == "confirm":
        # Handle confirmation
        datai = chat_session.send_message("give me all booking details in python dict as the date as DD/MM/YYYY and time as HH:MM 12 hrs format no extra text only dict as keys as up,down,time,date up contains only coordinates and down conatains only coordinates for example {'up': {'lat': 26.9026885, 'long': 75.7986445}, 'down': {'lat': 26.903216, 'long': 75.799425, 'name': 'Hari om shop'}, 'date': '30/09/2024', 'time': '05:45 PM'}")
        text = datai.text
        print(text)
        latitude_pattern = r"'lat':\s(-?[\d.]+)"
        longitude_pattern = r"'long':\s(-?[\d.]+)"
        date_pattern = r"'date':\s'([\d/]+)'"
        time_pattern = r"'time':\s'([\d:]+\s[APM]+)'"


        # Extract latitude and longitude
        latitudes = re.findall(latitude_pattern, text)
        longitudes = re.findall(longitude_pattern, text)

        # Extract date and time
        date = re.search(date_pattern, text).group(1)
        time = re.search(time_pattern, text).group(1)

        # Round latitudes and longitudes and convert them to floats
        up_coords = [round(float(latitudes[0]), 4), round(float(longitudes[0]), 4)]
        down_coords = [round(float(latitudes[1]), 4), round(float(longitudes[1]), 4)]

        # Combine into a list
        result = [up_coords, down_coords, time, date]
        print(result)
        data = { }
        data["pickup"] = result[0]
        data["dropoff"] = result[1]
        data["time"] = result[2]
        data["date"] = result[3]
        data["name"] = name
        data["phoneNo"] = wa_id
        
        # Check availability in API
        resp = estimate_fare(data)
        print(resp)

        if 'id' not in resp:
            return "slot is not Available"
        else:
            '''global api_data 
            api_data = []
            api_data.append(values[0])
            api_data.append(values[1])
            time = convert_time_date(values[2], values[3])
            ty = get_time_slot_availability(values[0], values[1], time)
            iso = convert_to_iso8601(time)
            api_data.append(iso)
            api_data.append(ty)
            if api_response_drop and api_response_pick and ty['availability']:'''
            current_state = "confirm_yes_no"
            response_text = f"We are servicing here and slot is also available, the fare is {resp['totalFare']}.{send_wati_sms(wa_id)}"
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history,current_state)
            booking_id = resp['id']
            push_booking(wa_id,booking_id)
            return response_text
        '''else:
            current_state = "booking"
            chat_session.send_message("confirm")
            return "we are not servicing here currently,you can check our servicable are at https://goblu-ev.com/service."'''

    elif current_state == "confirm_yes_no":
        if message_body_lower == "yes" and current_state == "confirm_yes_no":
            current_state = "enquiry"
            #res = book_cab(api_data[0],api_data[1],api_data[2],name,wa_id,api_data[3]['vehicle']['id'])
            #api_data = []
            
            response_text = "Congratulations! Your eco-friendly ride with GoBlu-EV has been confirmed. Driver details will be shared 30 mins before the ride starts. Check our app for the ride details. For any assistance call +61280024072 or mail support@gobluev.com. Have a safe ride."
            chat_session.send_message("confirm")
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history,current_state)
            current_state = None
            idt = get_most_recent_booking_id(wa_id)
            redf = book_ride(idt)
            return redf['message']
        elif message_body_lower == "no" and current_state == "confirm_yes_no":
            api_data = []
            current_state = "enquiry"
            response_text = "Booking cancelled!"
            chat_session.send_message("booking cancelled")
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history,current_state)
            current_state = None
            return response_text
        else:
            current_state = "confirm_yes_no"
            response_text = f"Invalid response. Please respond with 'yes' or 'no'.{send_wati_sms(wa_id)}"
            history.append({
                "role": "model",
                "parts": [response_text]
            })
            store_thread(wa_id, history,current_state)
            
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

def send_wati_sms_greet(number):
 
  WATI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1MzEwOTJiNy1hYjkxLTRjYTEtOTc0Yy00YzBiYjAyNDlkNjkiLCJ1bmlxdWVfbmFtZSI6ImluZm9AZ29ibHUtZXYuY29tIiwibmFtZWlkIjoiaW5mb0Bnb2JsdS1ldi5jb20iLCJlbWFpbCI6ImluZm9AZ29ibHUtZXYuY29tIiwiYXV0aF90aW1lIjoiMDIvMDEvMjAyNCAwNTo0ODoxNyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIxMTM5MTgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.uOPfYW9dl2pyTx42hSqfJ6EdP7RMCjfhTFGP0pQk5D0"
  base_url = "https://live-mt-server.wati.io/113918/api/v1/sendTemplateMessage"
  url = f"{base_url}?whatsappNumber={number}"
  
  headers = {
      "Authorization": f"Bearer {WATI_TOKEN}",
      "content-type": "Application/json",
  }

  data = {
      "broadcast_name": "welcome_message_v5",
      "template_name": "welcome_message_v5",
  }
  response = requests.post(url, headers=headers, json=data)
  print(response)
  print(response.text)
  return
    

def send_location_request_message(to):
    url = "https://graph.facebook.com/v20.0/368948182969171/messages"
    
    headers = {
        "Authorization": "Bearer EAAuXEbmPW2sBOZBLfFHJKCPAEVcfg2iHmqxkoxBZBLyhx48DXlDmrMEakZCNfhZBcVzBlPQZA8aUkyse0wKqSVyXC3eyDfLg9rTM4oSLnUHbPmjhZAZA8q3aB4ue3rHfmYrnZCHzQqwZAVKTCLlmJ5oXkySlxaZB6ksZBiU5wm2P9JB7yp519Ah5v4mLEpi2btcZB0ks065dZBKnZBGouI1ZCcp0w2BL5fSFbnVWHV4aHZBAMDT2",
        "Content-Type": "application/json"
    }

    # Payload for the request location message
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Please share your location with us for better service."
            },
            "action": {
                "buttons": [
                    {
                        "type": "location"
                    }
                ]
            }
        }
    }

    # Sending the POST request to the WhatsApp API
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Checking response status
    if response.status_code == 200:
        print("Location request message sent successfully!")
    else:
        print(f"Failed to send message. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def send_wati_sms(number):
 
  WATI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1MzEwOTJiNy1hYjkxLTRjYTEtOTc0Yy00YzBiYjAyNDlkNjkiLCJ1bmlxdWVfbmFtZSI6ImluZm9AZ29ibHUtZXYuY29tIiwibmFtZWlkIjoiaW5mb0Bnb2JsdS1ldi5jb20iLCJlbWFpbCI6ImluZm9AZ29ibHUtZXYuY29tIiwiYXV0aF90aW1lIjoiMDIvMDEvMjAyNCAwNTo0ODoxNyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIxMTM5MTgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.uOPfYW9dl2pyTx42hSqfJ6EdP7RMCjfhTFGP0pQk5D0"
  base_url = "https://live-mt-server.wati.io/113918/api/v1/sendTemplateMessage"
  url = f"{base_url}?whatsappNumber={number}"
  
  headers = {
      "Authorization": f"Bearer {WATI_TOKEN}",
      "content-type": "Application/json",
  }

  data = {
      "broadcast_name": "jayant_cofirm_or_cancel",
      "template_name": "jayant_cofirm_or_cancel",
  }
  response = requests.post(url, headers=headers, json=data)
  print(response)
  print(response.text)
  return
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
    
    '''url = "https://webapi.goblu-ev.com/v1/call/get_ride_fare"
    params = {
        "pickup_loc": pickup_loc,
        "drop_loc": drop_loc
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")'''
    return 40

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

import google.generativeai as genai
import shelve
import os
import uuid
import time
import logging

# Configure the API
genai.configure(api_key="AIzaSyB9PU1u_Pq8Fs2Q8cIYJWF3MMzlWmzfuVw")

# Define the generation configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="""you are whatsapp chat bot of goblu ev company which provides ev cabs in melbourne

Welcome Message

Welcome to GoBlu-EV! Enjoy our brand new noiseless and comfortable electric cars in Melbourne. How can we assist you today?

Services Information

At GoBlu-EV, we offer affordable and comfortable electric cab rides in Melbourne. Here’s what makes us special:

Noiseless and Comfortable: Enjoy a peaceful ride in our state-of-the-art electric vehicles.
Flat Pricing: We believe in fair pricing with no surge charges, no matter the demand.
Safety First: All our drivers undergo rigorous background checks, and our vehicles are equipped with advanced safety features. Your safety is our priority.
Would you like to book a ride or need more information?

Booking a Ride

Great! Let's get you a ride. Please provide the following details:

Pick-up location
Drop-off location
Desired time and date
Once we have these details, we'll confirm your booking.

About Us

At GoBlu-EV, our story begins with a passion for sustainable transportation and a commitment to creating a greener future. We recognized the urgent need to address the carbon emissions produced by traditional transportation methods in Australia. Our mission is to provide affordable, comfortable, and eco-friendly rides for everyone.

Would you like to know more about our services or book a ride?

Pricing Information

We believe in transparent and fair pricing. At GoBlu-EV, we offer flat rates with no surge charges, even during peak hours. Our rates are designed to be affordable and competitive, ensuring you get the best value for your money.

Would you like to get a quote for a specific journey or need further assistance?

Safety Measures

Your safety is our top priority at GoBlu-EV. Here's how we ensure a safe journey:

Background Checks: All our drivers undergo rigorous background checks.
Advanced Safety Features: Our vehicles are equipped with the latest safety technology.
Professional Drivers: Our drivers are trained to provide a safe and courteous service.
If you have any specific concerns or need more information, please let us know.

Contact Information

You can reach out to our support team at [insert contact email/phone number] for any assistance or inquiries. We’re here to help you 24/7.

Is there anything else you would like to know or need help with?

Feedback Collection

We hope you enjoyed your ride with GoBlu-EV. We would love to hear your feedback to help us improve our services. Please share your experience with us.

Thank you for choosing GoBlu-EV!
"""
)

def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        history = threads_shelf.get(wa_id, None)
        if history is not None and not isinstance(history, list):
            logging.error(f"Stored history for {wa_id} is not a list.")
            return None
        return history

def store_thread(wa_id, history):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = history

def run_assistant(history):
    # Flatten the history for the model input
    formatted_history = "\n".join(
        f"{entry['role']}: {entry['parts'][0]}"
        for entry in history
    )
    print("$$$$$$$$$$$$$$$$4$%^%$$%$%^$%@#@$#$@#$@")
    print(formatted_history)
    chat_session = model.start_chat()
    response = chat_session.send_message(formatted_history)
    return response

def generate_response(message_body, wa_id, name):
    # Check if there is already a thread for the wa_id
    history = check_if_thread_exists(wa_id)

    # If history is None or not a list, initialize a new one
    if history is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        history = [
            {"role": "user", "parts": ["hii\n"]},
            {"role": "model", "parts": ["Welcome to GoBlu-EV! Enjoy our brand new noiseless and comfortable electric cars in Melbourne. How can we assist you today? 🚕💨\n"]},
        ]
        store_thread(wa_id, history)
    else:
        logging.info(f"Retrieved existing thread for {name} with wa_id {wa_id}")

    # Add message to history
    history.append({"role": "user", "parts": [message_body]})

    # Run the assistant and get the new message
    new_message = run_assistant(history)

    # Add the assistant's response to history
    history.append({"role": "model", "parts": [new_message]})
    store_thread(wa_id, history)  # Update the stored history

    return new_message

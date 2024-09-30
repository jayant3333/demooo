import json

# Function to append a new booking_id (push to stack)
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

# Example usage
push_booking("waid_4", "booking_id_89")



# Function to get the most recent booking_id
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

# Example usage
wa_id = "waid_1"
recent_booking = get_most_recent_booking_id(wa_id)
print(f"Most recent booking for {wa_id}: {recent_booking}")


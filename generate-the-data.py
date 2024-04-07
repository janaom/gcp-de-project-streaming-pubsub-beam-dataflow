import random
import json
from datetime import datetime, timedelta

def generate_conversation():
    sender_types = ["Courier Android", "Customer iOS"]
    courier_id = random.randint(10000000, 99999999)
    customer_id = random.randint(10000000, 99999999)
    order_id = random.randint(10000000, 99999999)
    message_sent_time = "2024-02-01T10:00:00Z"  # Initial message sent time

    conversations = []
    chat_started_by_message = True  #Flag to track the first message in a conversation
    sender_type = random.choice(sender_types)
    num_replies = random.randint(2, 5)  #Random number of replies (2, 3, or 5)

    for message_num in range(2, num_replies + 2):
        order_stage = random.choice(["ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY", "RETURNED", "AWAITING_PICKUP", "ARRIVED", "FAILED", "PENDING", "ACCEPTED", "ON_ROUTE", "DELIVERED"])
        
        if sender_type.startswith("Courier"):
            conversation = {
                "senderAppType": sender_type,
                "courierId": courier_id,
                "fromId": courier_id,
                "toId": customer_id,
                "chatStartedByMessage": chat_started_by_message,
                "orderId": order_id,
                "orderStage": order_stage,
                "customerId": customer_id,
                "messageSentTime": message_sent_time
            }
        else:
            conversation = {
                "senderAppType": sender_type,
                "customerId": customer_id,
                "fromId": customer_id,
                "toId": courier_id,
                "chatStartedByMessage": chat_started_by_message,
                "orderId": order_id,
                "orderStage": order_stage,
                "courierId": courier_id,
                "messageSentTime": message_sent_time
            }
        
        conversations.append(conversation)
        chat_started_by_message = False  #Update flag for subsequent messages
        message_sent_time = increment_message_sent_time(message_sent_time)

        if sender_type.startswith("Courier"):
            sender_type = "Customer iOS"
        else:
            sender_type = "Courier Android"

    #Add additional line with city code
    city_line = {
        "orderId": order_id,
        "cityCode": random_city_code()
    }
    conversations.append(city_line)
    
    return conversations

def random_city_code():
    #Returns a random world city code
    city_codes = ["BCN", "NYC", "LON", "PAR", "BER", "TOK", "ROM", "MAD", "SYD", "MEX", "CAI", "AMS", "TOR", "IST", "SAN", "SIN", "RIO", "BUE", "CPT", "MUM"]
    return random.choice(city_codes)

def increment_message_sent_time(timestamp):
    #Increment the message sent time by a random duration between 1 minute and 15 minutes
    #Assumes the timestamp is in the format "YYYY-MM-DDTHH:MM:SSZ"
    message_sent_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    random_duration = random.randint(1, 15)  # Random duration in minutes
    message_sent_datetime += timedelta(minutes=random_duration)
    message_sent_time = message_sent_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return message_sent_time

#Generate 40000 conversations
all_messages = []
for _ in range(40000):
    messages = generate_conversation()
    all_messages.extend(messages)
    #Generate a new unique order ID for the next set of conversations
    order_id = random.randint(10000000, 99999999)

#Output conversations as JSON in a single line
output_filename = "conversations.json"
with open(output_filename, "w") as file:
    for message in all_messages:
        json.dump(message, file, separators=(",", ":"))
        file.write("\n")

print(f"{len(all_messages)} conversations generated and saved to {output_filename}.")

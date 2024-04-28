import random
from datetime import datetime, timedelta
import json

def generate_conversation():
    sender_types = ["Courier Android", "Customer iOS"]
    courier_id = random.randint(10000000, 99999999)
    customer_id = random.randint(10000000, 99999999)
    order_id = random.randint(10000000, 99999999)
    message_sent_time = generate_unique_time()  # Generate unique message sent time

    conversations = []
    chat_started_by_message = True  # Flag to track the first message in a conversation
    sender_type = random.choice(sender_types)
    num_replies = random.randint(2, 5)  # Random number of replies (2, 3, or 5)

    for message_num in range(num_replies):
        if sender_type.startswith("Courier"):
            conversation = {
                "senderAppType": sender_type,
                "courierId": courier_id,
                "fromId": courier_id,
                "toId": customer_id,
                "chatStartedByMessage": chat_started_by_message,
                "orderId": order_id,
                "orderStage": random.choice(["ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY", "RETURNED", "AWAITING_PICKUP", "ARRIVED", "FAILED", "PENDING", "ACCEPTED", "ON_ROUTE", "DELIVERED"]),
                "customerId": customer_id,
                "messageSentTime": message_sent_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        else:
            conversation = {
                "senderAppType": sender_type,
                "customerId": customer_id,
                "fromId": customer_id,
                "toId": courier_id,
                "chatStartedByMessage": chat_started_by_message,
                "orderId": order_id,
                "orderStage": random.choice(["ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY", "RETURNED", "AWAITING_PICKUP", "ARRIVED", "FAILED", "PENDING", "ACCEPTED", "ON_ROUTE", "DELIVERED"]),
                "courierId": courier_id,
                "messageSentTime": message_sent_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }

        conversations.append(conversation)
        chat_started_by_message = False  # Update flag for subsequent messages

        if sender_type.startswith("Courier"):
            sender_type = "Customer iOS"
        else:
            sender_type = "Courier Android"

        # Increment the message sent time by a random duration between 1 second and 1 minute
        message_sent_time += timedelta(seconds=random.randint(1, 60))

    # Add additional line with city code
    city_line = {
        "orderId": order_id,
        "cityCode": random_city_code()
    }
    conversations.append(city_line)

    return conversations

def generate_unique_time():
    global last_message_sent_time

    # Increment the last message sent time by a random duration between 1 second and 1 minute
    last_message_sent_time += timedelta(seconds=random.randint(1, 60))
    return last_message_sent_time

def random_city_code():
    cities = ["BCN", "NYC", "LON", "PAR", "BER", "TOK", "ROM", "MAD", "SYD", "MEX", "CAI", "AMS", "TOR", "IST", "SAN", "SIN", "RIO", "BUE", "CPT", "MUM"]
    return random.choice(cities)

# Set the initial message sent time
last_message_sent_time = datetime(2024, 2, 1, 10, 0, 0)

# Generate and save 400 conversations
conversations = []
for _ in range(400):
    conversation = generate_conversation()
    conversations.extend(conversation)

# Output conversations as JSON in a single line
output_filename = "conversations_400_single_line.json"
with open(output_filename, "w") as file:
    for message in conversations:
        json.dump(message, file, separators=(",", ":"))
        file.write("\n")

print("Conversations saved to 'conversations_400_single_line.json'")

#Example of the data
#{"senderAppType":"Courier Android","courierId":20067661,"fromId":20067661,"toId":49459478,"chatStartedByMessage":true,"orderId":69409879,"orderStage":"COMPLETED","customerId":49459478,"messageSentTime":"2024-02-01T10:00:07Z"}
#{"senderAppType":"Customer iOS","customerId":49459478,"fromId":49459478,"toId":20067661,"chatStartedByMessage":false,"orderId":69409879,"orderStage":"ACCEPTED","courierId":20067661,"messageSentTime":"2024-02-01T10:00:53Z"}
#{"senderAppType":"Courier Android","courierId":20067661,"fromId":20067661,"toId":49459478,"chatStartedByMessage":false,"orderId":69409879,"orderStage":"IN_PROGRESS","customerId":49459478,"messageSentTime":"2024-02-01T10:01:22Z"}
#{"orderId":69409879,"cityCode":"MUM"}
#{"senderAppType":"Customer iOS","customerId":62201746,"fromId":62201746,"toId":62321860,"chatStartedByMessage":true,"orderId":13379272,"orderStage":"COMPLETED","courierId":62321860,"messageSentTime":"2024-02-01T10:00:46Z"}
#{"senderAppType":"Courier Android","courierId":62321860,"fromId":62321860,"toId":62201746,"chatStartedByMessage":false,"orderId":13379272,"orderStage":"IN_PROGRESS","customerId":62201746,"messageSentTime":"2024-02-01T10:01:06Z"}
#{"orderId":13379272,"cityCode":"BER"}

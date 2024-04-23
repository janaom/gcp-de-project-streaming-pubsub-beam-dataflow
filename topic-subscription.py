from google.cloud import pubsub_v1

#Set your Google Cloud project ID
project_id = "streaming-project-415718"

#Set the topic and subscription names
topic_name = "topic-conversations"
subscription_name = "submessages"

#Create a publisher client
publisher_client = pubsub_v1.PublisherClient()

#Create a topic
topic_path = publisher_client.topic_path(project_id, topic_name)
topic = publisher_client.create_topic(request={"name": topic_path})

print(f"Topic created: {topic.name}")

#Create a subscriber client
subscriber_client = pubsub_v1.SubscriberClient()

#Create a subscription
subscription_path = subscriber_client.subscription_path(project_id, subscription_name)
subscription = subscriber_client.create_subscription(request={"name": subscription_path, "topic": topic_path})

print(f"Subscription created: {subscription.name}")

#an example of the output
#Topic created: projects/streaming-project-415718/topics/topic-conversations
#Subscription created: projects/streaming-project-415718/subscriptions/submessages

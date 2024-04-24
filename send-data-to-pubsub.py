from google.cloud import pubsub_v1
from google.cloud import storage
import time

#Create a publisher client
publisher = pubsub_v1.PublisherClient()
#Specify the topic path
topic_path = 'projects/streaming-project-415718/topics/topic-conversations'

#Get the topic
topic = publisher.get_topic(request={"topic": topic_path})
#Check if the topic exists
if topic is None:
    print('Topic does not exist:', topic_path)
    exit()

#Create a storage client
storage_client = storage.Client()

#Specify the bucket and file names
bucket_name = 'streaming-project'
file_name = 'conversations.json'

#Get the bucket and blob
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(file_name)

#Read the file line by line
with blob.open("r") as f_in:
    for line in f_in:
        #Data must be a bytestring
        data = line.encode('utf-8')
        #Publish the data to the topic
        future = publisher.publish(topic=topic.name, data=data)
        print(future.result())
        #Sleep for 1 second before publishing the next message
        time.sleep(1)

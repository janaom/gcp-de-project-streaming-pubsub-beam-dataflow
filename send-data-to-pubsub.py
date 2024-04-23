from google.cloud import pubsub_v1
from google.cloud import storage
import time

publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/streaming-project-415718/topics/topic-conversations'

topic = publisher.get_topic(request={"topic": topic_path})
if topic is None:
    print('Topic does not exist:', topic_path)
    exit()

storage_client = storage.Client()

bucket_name = 'streaming-project'
file_name = 'conversations.json'

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(file_name)

with blob.open("r") as f_in:
    for line in f_in:
        # Data must be a bytestring
        data = line.encode('utf-8')
        future = publisher.publish(topic=topic.name, data=data)
        print(future.result())
        time.sleep(1)

# <img width="40" alt="image" src="https://github.com/janaom/gcp-data-engineering-etl-with-composer-dataflow/assets/83917694/60f8f158-3bdc-4b3d-94ae-27a12441e2a3">  GCP Data Engineering Project: Streaming Data Pipeline with Pub/Sub and Apache Beam/Dataflow 📡

When it comes to streaming data, Kafka and Flink are popular topics of discussion. However, if you are working with Google Cloud Platform (GCP), it is more likely that you will utilize Pub/Sub, Apache Beam, and Dataflow as your primary streaming services. These tools can be used either standalone or in conjunction with other streaming solutions.

[Pub/Sub](https://cloud.google.com/pubsub/docs/overview) is an asynchronous and scalable messaging service that decouples services producing messages from services processing those messages. Pub/Sub is used for streaming analytics and data integration pipelines to load and distribute data. It's equally effective as a messaging-oriented middleware for service integration or as a queue to parallelize tasks.

[Dataflow](https://cloud.google.com/dataflow/docs/overview) is a Google Cloud service that provides unified stream and batch data processing at scale. Use Dataflow to create data pipelines that read from one or more sources, transform the data, and write the data to a destination. Dataflow is built on the open source Apache Beam project. Apache Beam lets you write pipelines using a language-specific SDK. Apache Beam supports Java, Python, and Go SDKs, as well as multi-language pipelines. Dataflow executes Apache Beam pipelines. If you decide later to run your pipeline on a different platform, such as Apache Flink or Apache Spark, you can do so without rewriting the pipeline code.
With prior experience in utilizing Beam for batch projects, I was keen to experiment with its streaming functionality. The following is a challenging task I came across and the corresponding solution I developed.

# 🚀 Data Pipeline Challenge

We have a "conversations.json" file containing the "customer_courier_chat_messages" event data, which includes information about individual messages exchanged between customers and couriers through the in-app chat. A sample of the event data is provided .

```json
{
    "senderAppType": "Courier Android",
    "courierId": 61404437,
    "fromId": 61404437,
    "toId": 40874303,
    "chatStartedByMessage": true,
    "orderId": 10000632,
    "orderStage": "IN_PROGRESS",
    "customerId": 40874303,
    "messageSentTime": "2024-02-01T10:00:00Z"
},
{
...
}
```

Additionally, you have access to the "orders" event, which contains the "orderId" and "cityCode" fields.

```json
{
    "orderId": 10000632,
    "cityCode": "MAD"
},
{
...
}
```

Using the prepared data, we will simulate the streaming of Courier and Customer conversations. We have 400 conversations in total, with the first message coming from either the Courier or the Customer. This initial message is followed by another important message that contains the "orderId" and "cityCode". Subsequent messages will then appear in chronological order, with each conversation consisting of 2–5 messages. If you're interested in the original data generation process, you can find the code on my GitHub repository. Here is an example of a complete conversation:

```json
{"senderAppType": "Courier Android", "courierId": 61404437, "fromId": 61404437, "toId": 40874303, "chatStartedByMessage": true, "orderId": 10000632, "orderStage": "IN_PROGRESS", "customerId": 40874303, "messageSentTime": "2024-02-01T10:00:00Z"}
{"orderId": 10000632, "cityCode": "MAD"}
<...>
{"senderAppType": "Customer iOS", "customerId": 40874303, "fromId": 40874303, "toId": 61404437, "chatStartedByMessage": false, "orderId": 10000632, "orderStage": "FAILED", "courierId": 61404437, "messageSentTime": "2024-02-01T10:08:00Z"}
<...>
{"senderAppType": "Courier Android", "courierId": 61404437, "fromId": 61404437, "toId": 40874303, "chatStartedByMessage": false, "orderId": 10000632, "orderStage": "FAILED", "customerId": 40874303, "messageSentTime": "2024-02-01T10:21:00Z"}
<...>
{"senderAppType": "Customer iOS", "customerId": 40874303, "fromId": 40874303, "toId": 61404437, "chatStartedByMessage": false, "orderId": 10000632, "orderStage": "ACCEPTED", "courierId": 61404437, "messageSentTime": "2024-02-01T10:35:00Z"}
```

Your task is to build a data pipeline to aggregate individual messages into conversations. Take into consideration that a conversation is unique per order. We aim to split the data into two tables: "conversations" and "orders". This separation will facilitate future analytics and data processing. The final table "customer_courier_conversations" should include the following required fields:

```
● order_id
● city_code
● first_courier_message: Timestamp of the first courier message
● first_customer_message: Timestamp of the first customer message
● num_messages_courier: Number of messages sent by courier
● num_messages_customer: Number of messages sent by customer
● first_message_by: The first message sender (courier or customer)
● conversation_started_at: Timestamp of the first message in the conversation
● first_responsetime_delay_seconds: Time (in secs) elapsed until the first message was responded
● last_message_time: Timestamp of the last message sent
● last_message_order_stage: The stage of the order when the last message was sent
```

In this project, I will present my solution and provide a detailed, step-by-step guide on how to accomplish this task. Our focus will be on building a streaming pipeline using various GCP services, which include:

![20240423_181509](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/cf670f64-eb28-4c9e-8d17-c4fb0e8bb36f)




<img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-connect-four-with-python-dataflow/assets/83917694/0887957d-db1b-4938-a9fa-f497fcebbeff"> Google Cloud Storage (GCS) is used to store the "conversations.json" file. It provides reliable and scalable object storage for your data.

<img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/c0f07cb2-e512-48da-b201-19c6e255c6c0"> Pub/Sub is used to publish the contents of the "conversations.json" file to a specified topic, allowing for asynchronous communication and decoupling of message producers and consumers. It ensures reliable and scalable message delivery.


<img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-connect-four-with-python-dataflow/assets/83917694/5df502de-1936-42fb-a3d5-2fa7cf0c5723"> Dataflow, built on the Apache Beam framework, is used to construct and run a streaming data processing pipeline. It facilitates the real-time transformation of conversations data. By leveraging Dataflow, we can effectively divide the data into two tables: "conversations" and "orders".


<img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-connect-four-with-python-dataflow/assets/83917694/7c95b56f-a1fc-49b3-8e96-ed607f2094ea"> BigQuery is used to store the processed conversations data. It provides a scalable and efficient platform for querying and analyzing the streaming data, allowing for insightful data retrieval and analysis.

<img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/dd989c11-cbb0-43c4-814c-6237e23550f1"> Terraform is used to define and provision a GCS bucket, Pub/Sub topic, subscription, and BigQuery dataset with tables. It enables the automation of resource creation, ensuring a consistent and reproducible infrastructure setup for efficient data storage, messaging, and analysis.


# <img width="20" alt="image" src="https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/dd989c11-cbb0-43c4-814c-6237e23550f1">  Terraform
To streamline the process, I've included Terraform files that enable the automation of several components within the GCP environment. By utilizing Terraform, you can efficiently create the following resources: GCS bucket, bucket object, Pub/Sub topic, subscription, BigQuery dataset, tables. Incorporating Terraform into your workflow is an excellent opportunity to explore Infrastructure as Code (IaaC) or reinforce your existing knowledge. The files are available in the Terraform folder on my GitHub account. Alternatively, you can manually set up these services if you prefer not to use Terraform automation.

When working within GCP, there's no need to install Terraform. Simply execute the following basic commands: `terraform init`, `terraform plan`, `terraform apply`, and `terraform destroy`.
For more advanced parameters and customization options, refer to the [Terraform Registry](https://registry.terraform.io/).

# 📡 Pub/Sub: Topic and Subscription
To gain a better understanding of Pub/Sub's functionality, refer to the message lifecycle example, which illustrates how messages are transmitted through the system.

![1 FKjozGDmbCruoEg8Y3-DFw](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/8f359787-9d7b-432d-b51a-fb56cf8107d6)

A publisher application sends a message to a Pub/Sub topic. The message is written to storage. Along with writing the message to storage, Pub/Sub delivers the message to all the attached subscriptions of the topic. In this example, it's a single subscription. The subscription sends the message to an attached subscriber application. The subscriber sends an acknowledgment to Pub/Sub that they have processed the message.

We have several options for creating the Pub/Sub topic and subscription:

- Utilize the GCP console to manually set up the Topic and Subscription.

![1 j9P0AkzfCtDNglLFK4v9Cw](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/23107a5b-3fb8-4706-91c2-f4dea26eec64)

![1 ZpJZU_9gZ5muokgMOWpzPA](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/4bab328b-c4d5-4fbf-babd-408a1101d5aa)

- Leverage the provided code in my repository by running the command `python topic-subscription.py`.
  
- Employ the Terraform code with the `main.tf` file to automate and control the creation of resources.

Each method has its advantages, and you can choose the one that best suits your preferences and project requirements.

# 🔊 Sending Data to Pub/Sub
We have several options for transmitting data from the bucket to Pub/Sub:
- Export the data directly from the bucket to Pub/Sub.

![1 YXSdUQNBLiDKkxVOyoMt3A](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/b00eb19d-2d0c-457a-af7f-7923fe8ab679)

- Import the data directly from the topic to Pub/Sub.

![1 IMJXLiuBm0VZlZ3nH0C5ew](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/d08dff32-6a5f-4207-a9f4-209ca5d800ae)

Both methods involve initiating a Dataflow batch job and utilizing the 'Cloud Storage Text File to Pub/Sub (Batch)' template. However, these options are most suitable for handling smaller datasets.

If you're working with larger data volumes, alternative methods are required to efficiently send data to Pub/Sub. In such cases, I recommend employing Python code. This approach is more effective for managing and processing substantial amounts of data.

Execute the code by running the command `python send-data-to-pubsub.py` in your first terminal. Ensure to provide the necessary parameters: topic path, bucket name, and file name.

![20240406_201746](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/33fcace5-3f6e-4942-8806-2d476ffee20b)


# <img width="40" alt="image" src="https://beam.apache.org/images/mascot/beam_mascot_500x500.png"> Streaming Apache Beam/Dataflow pipeline

Apache Beam is a versatile framework that offers flexibility for both batch and streaming data processing, making it a widely applicable tool in various use cases.

The [Direct Runner](https://beam.apache.org/documentation/runners/direct/) executes pipelines on your machine and is designed to validate that pipelines adhere to the Apache Beam model as closely as possible. Using the Direct Runner for testing and development helps ensure that pipelines are robust across different Beam runners. The Direct Runner is not designed for production pipelines, because it's optimized for correctness rather than performance.

The Google Cloud [Dataflow Runner](https://beam.apache.org/documentation/runners/dataflow/) uses the Cloud Dataflow managed service. When you run your pipeline with the Cloud Dataflow service, the runner uploads your executable code and dependencies to a Google Cloud Storage bucket and creates a Cloud Dataflow job, which executes your pipeline on managed resources in Google Cloud Platform.

Transforming your Apache Beam pipeline from DirectRunner to DataflowRunner for creating a Dataflow job is a straightforward process that requires just a few modifications. The `job_name` and other lines after it in the following code are optional. However, you may want to consider adjusting the number of workers to enhance the job's performance. For more information on Pipeline options, refer to [this documentation](https://cloud.google.com/dataflow/docs/reference/pipeline-options#python).

If you want to specify a Service account, make sure it has these roles: BigQuery Admin, Dataflow Worker, Pub/Sub Admin, Storage Object Viewer.

```python
<...>
#Define your Dataflow pipeline options
options = PipelineOptions(
    runner='DirectRunner',     #for Dataflow job change to DataflowRunner
    project='your-project-id',
    region='US',     #for Dataflow job change to e.g. us-west1
    temp_location='gs://your-bucket/temp',
    staging_location='gs://your-bucket/staging',
    streaming=True,    #Enable streaming mode
    #Dataflow parameters that are optional
    #job_name='streaming-conversations'   
    #num_workers=5,    
    #max_num_workers=10,    
    #disk_size_gb=100,    
    #autoscaling_algorithm='THROUGHPUT_BASED',    
    #machine_type='n1-standard-4',    
    #service_account_email='your-service-account@your-project.iam.gserviceaccount.com'  
<...>
```

Autoscaling will be enabled for Dataflow Streaming Engine even without specifying optional parameters. Workers will scale between 1 and 100 unless maxNumWorkers is specified.

![1 N3Gf-klbpfYAaC79hOQeuA](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/250cfed1-3fe7-46a6-b0b5-c197b2b2948f)

Execute the code in your second terminal by running the following command: `python streaming-beam-dataflow.py`. This will allow you to start the streaming process using Apache Beam and/or Dataflow.

Executing the provided code (`python send-data-to-pubsub.py` and `python streaming-beam-dataflow.py`) in each terminal will trigger a series of actions:
- We publish the messages to the Pub/Sub topic.
- The pipeline reads data from a Pub/Sub subscription using the `ReadFromPubSub` transform.
- The desired fields from the parsed messages are extracted for the "conversations" and "orders" tables using the `beam.Map` transform and lambda functions.
- The processed "conversations" and "orders" data is written to the respective BigQuery tables using the `WriteToBigQuery` transform.

# ⏯️ BigQuery Streaming Buffer
By default, BigQuery stores streaming data in a special storage location called the "streaming buffer." The streaming buffer is a temporary storage area that holds the incoming data for a short period before it is fully committed and becomes part of the permanent table.

![1 g4PjtluUvzrwRtpdpEziEA](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/0d5b4e86-c01b-485b-b7c5-8a88d07e4f3a)


When you stop streaming data, the data in the streaming buffer is no longer continuously updated. BigQuery then starts the process of flushing the buffered data into the main table storage. The data is also reorganized and compressed for efficient storage. This process ensures data consistency and integrity before fully committing it to the table.

The time it takes for the streamed data to be fully committed and visible in the table depends on various factors, including the size of the buffer, the volume of data, and BigQuery's internal processing capacity. Typically, it takes a few minutes or up to 90 minutes for the streaming buffer to be completely flushed and the data to be visible in the table.

In the provided example, the updated information becomes visible in the "Storage info" section.

![1 NDYjPiI7HAgPbLboYfIVRw](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/ceb1dcfd-22a2-4073-b237-3021b0e86dc0)


# 🧮 Querying the Final Table
The final step involves creating the "customer_courier_conversations" table. In this case, we will generate a [view](https://cloud.google.com/bigquery/docs/views-intro), which is a virtual table defined by a SQL query. The custom SQL code will help transform the data to meet the specific task requirements.

![1 7SFCGTdJLBsjC1I7am3h7Q](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/b7b88fdd-0272-401c-ab25-e754c5345a20)


Views are virtual references to a set of data, offering reusable access without physically storing the data. [Materialized views](https://cloud.google.com/bigquery/docs/materialized-views-intro), on the other hand, are defined using SQL like regular views but physically store the data. However, they come with [limitations](https://cloud.google.com/bigquery/docs/materialized-views-intro#comparison) in query support. Due to the substantial size of my query, opting for a regular view was the more suitable choice in this case.

Once the streaming process has been initiated, you can execute the saved view after a brief interval.

```sql
SELECT * FROM `your-project-id.dataset.view`
```

Let's examine the first row from the results by extracting all messages associated with the "orderId" 77656162 from the "conversations.json" file.

![1 G-LpAKxAmGHTShp743ed7A](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/74e59371-a38f-42ff-a6e6-e80dfa871b1b)


The analysis yielded the following results: a total of 5 messages were identified. The conversation commenced with a Courier message in Rome at 10:04:46. The Customer responded after 42 seconds, at 10:05:28. The final message was received from the Courier at 10:06:35, and the last message order stage was recorded as "FAILED".

```json
{"senderAppType": "Courier Android", "courierId": 45035010, "fromId": 45035010, "toId": 57270753, "chatStartedByMessage": true, "orderId": 77656162, "orderStage": "AWAITING_PICKUP", "customerId": 57270753, "messageSentTime": "2024-02-01T10:04:46Z"}
{"orderId": 77656162, "cityCode": "ROM"}
{"senderAppType": "Customer iOS", "customerId": 57270753, "fromId": 57270753, "toId": 45035010, "chatStartedByMessage": false, "orderId": 77656162, "orderStage": "DELAYED", "courierId": 45035010, "messageSentTime": "2024-02-01T10:05:28Z"}
{"senderAppType": "Courier Android", "courierId": 45035010, "fromId": 45035010, "toId": 57270753, "chatStartedByMessage": false, "orderId": 77656162, "orderStage": "ACCEPTED", "customerId": 57270753, "messageSentTime": "2024-02-01T10:05:31Z"}
{"senderAppType": "Customer iOS", "customerId": 57270753, "fromId": 57270753, "toId": 45035010, "chatStartedByMessage": false, "orderId": 77656162, "orderStage": "DELAYED", "courierId": 45035010, "messageSentTime": "2024-02-01T10:06:16Z"}
{"senderAppType": "Courier Android", "courierId": 45035010, "fromId": 45035010, "toId": 57270753, "chatStartedByMessage": false, "orderId": 77656162, "orderStage": "FAILED", "customerId": 57270753, "messageSentTime": "2024-02-01T10:06:35Z"}
```

Please note that, in my case, the time difference between the first and last messages was only 2 minutes, resulting in a relatively quick analysis. As new data is continuously streaming into the source, the view is automatically updated in real-time to reflect the changes. This means that whenever you query the view, you will get the most up-to-date data that matches the defined criteria.

To gain further insights into the dynamic nature of the streaming process, let's examine additional examples and observe how the results evolve over time.

![1 QRnvMHwBdOKcmfP11bWeXw](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/bbfdd566-6cb2-49ea-ba0f-110ababd7f60)


In the first example, the conversation associated with "orderId" 66096282 in Tokyo commenced with a Courier message at 10:38:50. At this point, no response from the Customer has been received. The last message order stage is shown as "OUT_FOR_DELIVERY".

To observe any changes, let's execute the view once again and compare the results.

![1 zROM0ndny_c4DQRkz0mTdg](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/289c77a2-37e4-4650-add1-bd0bfa0f6e13)


A Customer reply was received at 10:39:30. Although the view indicates that the last message was sent at 10:39:45 with the status "PENDING", a closer examination of the JSON file reveals that the actual last message will be sent at 10:41:07, which hasn't been received yet. Additionally, expect the number of messages to be updated shortly.

Let's execute the view one more time.

![1 jV6tijubvOGB6-xjfQLTbQ](https://github.com/janaom/gcp-de-project-streaming-beam-dataflow-pubsub/assets/83917694/205087dc-4963-427d-95a1-be4a552aae1b)

Here we see that all 5 messages have been received, and the last message order stage now is "ACCEPTED". 🥳

```json
{"senderAppType": "Courier Android", "courierId": 64897260, "fromId": 64897260, "toId": 55461000, "chatStartedByMessage": true, "orderId": 66096282, "orderStage": "OUT_FOR_DELIVERY", "customerId": 55461000, "messageSentTime": "2024-02-01T10:38:50Z"}
{"orderId": 66096282, "cityCode": "TOK"}
{"senderAppType": "Customer iOS", "customerId": 55461000, "fromId": 55461000, "toId": 64897260, "chatStartedByMessage": false, "orderId": 66096282, "orderStage": "ACCEPTED", "courierId": 64897260, "messageSentTime": "2024-02-01T10:39:30Z"}
{"senderAppType": "Courier Android", "courierId": 64897260, "fromId": 64897260, "toId": 55461000, "chatStartedByMessage": false, "orderId": 66096282, "orderStage": "PENDING", "customerId": 55461000, "messageSentTime": "2024-02-01T10:39:45Z"}
{"senderAppType": "Customer iOS", "customerId": 55461000, "fromId": 55461000, "toId": 64897260, "chatStartedByMessage": false, "orderId": 66096282, "orderStage": "IN_PROGRESS", "courierId": 64897260, "messageSentTime": "2024-02-01T10:40:37Z"}
{"senderAppType": "Courier Android", "courierId": 64897260, "fromId": 64897260, "toId": 55461000, "chatStartedByMessage": false, "orderId": 66096282, "orderStage": "ACCEPTED", "customerId": 55461000, "messageSentTime": "2024-02-01T10:41:07Z"}
```


To experiment with larger data, you can access the `generate-the-data.py` code on my GitHub repository. This code allows you to generate additional conversations, enabling you to test the project's scalability.🤖

If you have any questions or would like to discuss streaming, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/jana-polianskaja/)! I'm always open to sharing ideas and engaging in insightful conversations.😊

Throughout this article, I've referred to the following sources for specific details and concepts:

https://cloud.google.com/dataflow/docs/overview

https://cloud.google.com/pubsub/docs/overview

https://beam.apache.org/documentation/runners/dataflow/

https://beam.apache.org/documentation/runners/direct/

https://cloud.google.com/bigquery/docs/views-intro







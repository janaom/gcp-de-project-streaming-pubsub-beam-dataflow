#run with python my-streaming-dataflow.py --streaming

import apache_beam as beam
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery
import json
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import Sessions

#Define your Dataflow pipeline options
options = PipelineOptions(
    runner='DirectRunner',   #for Dataflow job change to runner='DataflowRunner'
    project='streaming-project-415718',
    region='US',   #for Dataflow job change to 'us-central1'
    temp_location='gs://streaming-project-415718/temp',
    staging_location='gs://streaming-project-415718/staging',
    streaming=True  #Enable streaming mode
)

#Define your Beam pipeline
with beam.Pipeline(options=options) as pipeline:
    #Read the input data from Pub/Sub
    messages = pipeline | ReadFromPubSub(subscription='projects/streaming-project-415718/subscriptions/submessages')

    #Parse the JSON messages
    parsed_messages = messages | beam.Map(lambda msg: json.loads(msg))

    #Extract the desired fields for 'conversations' table
    conversations_data = parsed_messages | beam.Map(lambda data: {
        'senderAppType': data.get('senderAppType', 'N/A'),
        'courierId': data.get('courierId', None),
        'fromId': data.get('fromId', None),
        'toId': data.get('toId', None),
        'chatStartedByMessage': data.get('chatStartedByMessage', False),
        'orderId': data.get('orderId', None),
        'orderStage': data.get('orderStage', 'N/A'),
        'customerId': data.get('customerId', None),
        'messageSentTime': data.get('messageSentTime', '1970-01-01T00:00:00Z'),
    }) | beam.Filter(lambda data: data['orderId'] is not None and data['customerId'] is not None)

    #Extract the desired fields for 'orders' table
    orders_data = parsed_messages | beam.Map(lambda data: {
        'cityCode': data.get('cityCode', 'N/A'),
        'orderId': data.get('orderId', None),
    }) | beam.Filter(lambda data: data['orderId'] is not None and data['cityCode'] != 'N/A')

    #Define the schema for the 'conversations' table
    conversations_schema = {
        'fields': [
            {'name': 'senderAppType', 'type': 'STRING'},
            {'name': 'courierId', 'type': 'INTEGER'},
            {'name': 'fromId', 'type': 'INTEGER'},
            {'name': 'toId', 'type': 'INTEGER'},
            {'name': 'chatStartedByMessage', 'type': 'BOOLEAN'},
            {'name': 'orderId', 'type': 'INTEGER'},
            {'name': 'orderStage', 'type': 'STRING'},
            {'name': 'customerId', 'type': 'INTEGER'},
            {'name': 'messageSentTime', 'type': 'TIMESTAMP'}
        ]
    }

    #Define the schema for the 'orders' table
    orders_schema = {
        'fields': [
            {'name': 'cityCode', 'type': 'STRING'},
            {'name': 'orderId', 'type': 'INTEGER'}
        ]
    }

    #Apply session windows based on customer ID for 'conversations' table
    sessioned_conversations_data = conversations_data | 'Session window for the conversation table' >> beam.WindowInto(
        Sessions(gap_size=3600),
        trigger=beam.trigger.AfterWatermark(),
        accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING
    )

    #Apply session windows based on customer ID for 'orders' table
    sessioned_orders_data = orders_data | 'Session window for the orders table' >> beam.WindowInto(
        Sessions(gap_size=3600),
        trigger=beam.trigger.AfterWatermark(),
        accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING
    )

    #Write the conversations data to the 'conversations' table in BigQuery
    sessioned_conversations_data | 'Write conversations to BigQuery' >> WriteToBigQuery(
        table='streaming-project-415718:data_conversations.conversations',
        schema=conversations_schema,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
    )

    #Write the orders data to the 'orders' table in BigQuery
    sessioned_orders_data | 'Write orders to BigQuery' >> WriteToBigQuery(
        table='streaming-project-415718:data_conversations.orders',
        schema=orders_schema,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
    )

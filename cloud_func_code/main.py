def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    import base64
    import json
    from google.cloud import pubsub_v1
    # Instantiates a Pub/Sub client
    publisher = pubsub_v1.PublisherClient()
    PROJECT_ID = "jtoro-test"
    topic_name = "jtoro-test-topic"  
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)
    file_name = bytes(event['name'], 'utf-8')
    try:
        publish_future = publisher.publish(topic_path, data=file_name)
        publish_future.result()  # Verify the publish succeeded
        return 'Message published.'
    except Exception as e:
        print(e)
        return (e, 500)

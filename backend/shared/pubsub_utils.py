'''
Module for PubSub Utils
'''
from google.cloud import pubsub_v1

#pylint: disable=E1101
PROJECT_ID = "pursu-275920"
TOPIC_NAME = "pursu-topic"

def create_topic():
    '''Create a topic for pubsub'''
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

    topic = publisher.create_topic(topic_path)

    print("Topic created: {}".format(topic))

def create_subscriber(sub_name):
    '''Create a subscriber to project topic with given sub_name'''
    subscription_name = sub_name

    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(PROJECT_ID, TOPIC_NAME)
    subscription_path = subscriber.subscription_path(
        PROJECT_ID, subscription_name
    )

    subscription = subscriber.create_subscription(
        subscription_path, topic_path
    )

    print("Subscription created: {}".format(subscription))

    subscriber.close()


# Note: not necessary for our current configuration, we are using push subscribers
def configure_pull_subscription():
    '''Method to configure pull subscription'''

    subscription_name = "test_sub1"
    timeout = 5.0  # "How long the subscriber should listen for

    subscriber = pubsub_v1.SubscriberClient()

    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path(
        PROJECT_ID, subscription_name
    )

    def callback(message):
        print("Received message: {}".format(message))
        message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print("Listening for messages on {}..\n".format(subscription_path))

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except Exception as err:
            print(err)
            streaming_pull_future.cancel()

    print("Complete")

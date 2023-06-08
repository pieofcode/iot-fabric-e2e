# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import json
import signal
import threading
from azure.iot.device import IoTHubModuleClient, Message

from mqtt_utils import *

# global counters
SENT_IMAGES = 0

# global client
CLIENT = None

# Event indicating client stop
stop_event = threading.Event()


def create_client():

    try:
        client = IoTHubModuleClient.create_from_edge_environment()

        # Define function for handling received messages
        async def receive_message_handler(message):
            # NOTE: This function only handles messages sent to "input1".
            # Messages sent to other inputs, or to the default, will be discarded
            if message.input_name == "input1":
                print("the data in the message received on input1 was ")
                print(message.data)
                print("custom properties are")
                print(message.custom_properties)
                print("forwarding mesage to output1")
                await client.send_message_to_output(message, "output1")

        # Set handler on the client
        # client.on_message_received = receive_message_handler

    except Exception as iothub_error:
        print("Unexpected error {} from IoTHub".format(iothub_error))
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)

# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json


def send_to_hub(strMessage):
    message = Message(bytearray(strMessage, 'utf8'))
    CLIENT.send_message_to_output(message, "output1")
    global SENT_IMAGES
    SENT_IMAGES += 1
    print("Total images sent: {}".format(SENT_IMAGES))


def on_mqtt_message(client, userdata, msg):
    # message = json.loads(msg.payload.decode())
    logging.info(
        f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    msg = json.loads(msg.payload.decode())
    msg['module'] = 'MQTT'

    send_to_hub(msg.payload.decode())


def main():
    if not sys.version >= "3.5.3":
        raise Exception(
            "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version)
    print("IoT Hub Client for Python")

    # NOTE: Client is implicitly connected due to the handler being set on it
    global CLIENT
    CLIENT = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Subscribe to the external MQTT Broker
    mqtt_client = MQTTUtils.connect_mqtt(broker, port)
    MQTTUtils.subscribe(
        mqtt_client, "iotedge/edgeinspect/event", handler=on_mqtt_message)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(CLIENT))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(CLIENT.shutdown())
        loop.close()


if __name__ == "__main__":
    main()

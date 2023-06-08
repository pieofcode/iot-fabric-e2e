import os
import time
import random
import json
import sys
import logging
from paho.mqtt import client as mqtt_client

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'
)

# broker = "localhost"
broker = "172.17.0.1"
# broker = "host.docker.internal"
port = 1883

topic = "iotedge/edgeinspect/event"


# username = "iot-edgeinspect"
# passowrd = "@zdr126"

class MQTTUtils:

    @staticmethod
    def connect_mqtt(broker, port=1883, client_id=None):
        if client_id is None:
            client_id = f'edgeinspect-mqtt-{random.randint(0, 1000)}'

        client = mqtt_client.Client(client_id=client_id)
        # client.username_pw_set(username=username, password=password)
        client.on_connect = MQTTUtils.on_connect
        client.connect(broker, port)

        return client

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if (rc == 0):
            logging.info(f"Connected to {broker}:{port}")
        else:
            logging.error(f"Error while connecting - {rc}")

    @staticmethod
    def publish(client: mqtt_client, msg):
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            logging.info(f"Sending message to {topic} successful")
        else:
            logging.error(f"Failed to send message to {topic}")

    @staticmethod
    def subscribe(client: mqtt_client, topic, handler=None):
        client.subscribe(topic)
        if (handler == None):
            client.on_message = MQTTUtils.on_message
        else:
            client.on_message = handler

    @staticmethod
    def on_message(client, userdata, msg):
        logging.info(
            f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


def run_test(mode):
    client = MQTTUtils.connect_mqtt(broker, port)

    msg_count = 0
    if mode == "pub":
        client.loop_start()
        logging.info("Starting client in the publishing mode")
        while True:
            time.sleep(2)
            msg = f"message: {msg_count}"
            MQTTUtils.publish(client, msg)
            msg_count += 1

    elif mode == "sub":
        MQTTUtils.subscribe(client, topic)

    else:
        logging.warning(
            f"Invalid mode: {mode}. Please specify a valid mode values [pub, sub]")
        exit(0)

    client.loop_forever()


if __name__ == '__main__':
    mode = sys.argv[1]
    run_test(mode)

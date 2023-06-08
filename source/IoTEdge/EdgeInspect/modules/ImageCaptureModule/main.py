# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

from datetime import datetime
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import sys
import os
import requests
import json
from azure.iot.device import IoTHubModuleClient, Message
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from faker import Faker
from image_generator import test_func, ImageGenerator
from sql_utils import SQLManager

Faker.seed(0)
fake = Faker()

# global counters
SENT_IMAGES = 0
IMAGE_CAPTURE_DELAY_IN_SECONDS = 300
TWIN_CALLBACKS = 0


# global client
CLIENT = None

sql_manager = None


# Create local storage container
def create_container(connection_str, container_name):
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_str)  # , api_version="2022-11-02"
    # blob_service_client = BlobServiceClient(
    #     account_url="http://blobstoragemodule:11002/localstore", credential="imq92sFgNLrMSUQxkYyR1Q==", api_version="2021-10-04")

    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except ResourceExistsError as re:
        # Container already created
        print(f"Container [{container_name}] already created!")

    return container_client


# Upload blob
def upload_blob(container_client, file, metadata):
    # Upload a blob to the container
    ts = datetime.utcnow()
    partition = f"{ts.year}/{ts.month}/{ts.day}/{ts.hour}"
    with open(file, "rb") as data:
        print(f"Uploading file [{file}] with {data}")
        blob_client = container_client.upload_blob(
            name=f"{partition}/{os.path.basename(file)}", data=data)
        # Set metadata
        blob_client.set_blob_metadata(metadata)

# Define function for handling received twin patches


def receive_twin_patch_handler(twin_patch):
    global IMAGE_CAPTURE_DELAY_IN_SECONDS
    global TWIN_CALLBACKS
    print("Twin Patch received")
    print("     {}".format(twin_patch))
    if "TemperatureThreshold" in twin_patch:
        IMAGE_CAPTURE_DELAY_IN_SECONDS = twin_patch["imageCaptureDelayInSeconds"]
        print(
            f"New settings for IMAGE_CAPTURE_DELAY_IN_SECONDS: {IMAGE_CAPTURE_DELAY_IN_SECONDS} ")

    TWIN_CALLBACKS += 1
    print("Total calls confirmed: {}".format(TWIN_CALLBACKS))


# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json
def send_to_hub(strMessage):
    message = Message(bytearray(strMessage, 'utf8'))
    CLIENT.send_message_to_output(message, "output1")
    global SENT_IMAGES
    SENT_IMAGES += 1
    print("Total images sent: {}".format(SENT_IMAGES))


# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            print(
                f"Type of image data: [{type(test_image)}]. Content: {test_image}")
            response = requests.post(
                imageProcessingEndpoint, headers=headers, data=test_image)
            print("Response from classification service: (" +
                  str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("No response from classification service")
            return None

    return response.json()


# Define function for handling received twin patches
def receive_twin_patch_handler(twin_patch):
    global IMAGE_CAPTURE_DELAY_IN_SECONDS
    global TWIN_CALLBACKS
    print(f"Twin Patch received - {twin_patch}")
    if "initConfig" in twin_patch:
        init_config = twin_patch["initConfig"]
        IMAGE_CAPTURE_DELAY_IN_SECONDS = init_config["imageCaptureDelayInSeconds"]
        print(
            f"New settings for IMAGE_CAPTURE_DELAY_IN_SECONDS: {IMAGE_CAPTURE_DELAY_IN_SECONDS} ")

    TWIN_CALLBACKS += 1
    print("Total calls confirmed: {}".format(TWIN_CALLBACKS))

# Define function for handling received messages


def receive_message_handler(message):
    global RECEIVED_MESSAGES
    print(f"Message received: {message}")


def append_capture_log(metadata):
    global sql_manager
    params = [
        metadata["id"],
        metadata["orientation"],
        metadata["file_path"],
        metadata["tag"],
        json.dumps(metadata["classification"]),
        metadata["created_on"]
    ]

    sql_manager.insert_log(params)


def main(imageRootPath, imageProcessingEndpoint, localStorageConnStr, containerName, sqlDBHost, sqlPwd):
    global IMAGE_CAPTURE_DELAY_IN_SECONDS
    global TWIN_CALLBACKS
    global sql_manager

    try:
        print("Simulated camera module for Azure IoT Edge. Press Ctrl-C to exit.")

        try:
            global CLIENT
            CLIENT = IoTHubModuleClient.create_from_edge_environment()
            # Set handler on the client
            CLIENT.on_twin_desired_properties_patch_received = receive_twin_patch_handler
            CLIENT.on_message_received = receive_message_handler

        except Exception as iothub_error:
            print("Unexpected error {} from IoTHub".format(iothub_error))
            CLIENT.shutdown()
            raise

        print("The sample is now sending images for processing and will indefinitely.")

        image_file_list = ImageGenerator.get_all_images(imageRootPath, "parts")
        print(f"Image file list: {image_file_list}")

        orientation_list = ImageGenerator.get_all_orientation()
        print(f"Image file list: {orientation_list}")

        # Create container if not exist
        container_client = create_container(localStorageConnStr, containerName)
        print(f"Container client is created for: {containerName}")

        time.sleep(10)
        print("Setup a database table for log capture")
        # sql_manager = SQLManager(sqlDBHost, sqlPwd)

        # Create a database
        # sql_manager.create_db_table()

        while True:
            # Generate the random images with their orientation for the inferrence
            image_file_name = random.choice(image_file_list)
            orientation = random.choice(orientation_list)

            image_output_path, metadata = ImageGenerator.get_image(
                image_file_name, orientation)
            print(
                f"Inferrence endpoint invokved for: {image_output_path}, Orientation: {orientation}")

            classification = sendFrameForProcessing(
                image_output_path, imageProcessingEndpoint)
            print(f"Inferrence Response: {classification}")

            if classification:
                print("Image Classification is successful")
                map = {}
                for i in classification["predictions"]:
                    map[f'{i["tagName"]}Score'] = str(i["probability"])

                metadata["classification"] = classification
                metadata["classifiedOn"] = classification["created"]
                metadata.update(map)

                print(f"Metadata: {metadata}")
                send_to_hub(json.dumps(metadata))

                # Write the captured image to the blob store
                upload_blob(container_client, image_output_path, map)

                # Write log message into SQL DB
                # append_capture_log(metadata)

            else:
                print("Error while running the classification")

            time.sleep(IMAGE_CAPTURE_DELAY_IN_SECONDS)

    except KeyboardInterrupt:
        print("IoT Edge module sample stopped")


if __name__ == '__main__':

    try:

        # Retrieve the image location and image classifying server endpoint from container environment
        IMAGE_ROOT_PATH = os.getenv('IMAGE_ROOT_PATH', "")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")

        LOCAL_STORAGE_CONNECTION_STR = os.getenv(
            'LOCAL_STORAGE_CONNECTION_STR', "")
        CONTAINER_NAME = os.getenv('CONTAINER_NAME', "")

        SQLDB_HOSTNAME = os.getenv('SQLDB_HOSTNAME', "AzureSQLEdge")
        SQLDB_PWD = os.getenv('SQLDB_PWD', "")

        print(
            f"Initialized the module with Image Root Directory: {IMAGE_ROOT_PATH}, Image classifier endpoint: {IMAGE_PROCESSING_ENDPOINT}")

        print(
            f"Local Storage Connection string: {LOCAL_STORAGE_CONNECTION_STR}")
        print(f"Local Storage Container name: {CONTAINER_NAME}")

    except ValueError as error:
        print(error)
        sys.exit(1)

    if ((IMAGE_ROOT_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main(IMAGE_ROOT_PATH, IMAGE_PROCESSING_ENDPOINT,
             LOCAL_STORAGE_CONNECTION_STR, CONTAINER_NAME, SQLDB_HOSTNAME, SQLDB_PWD)
    else:
        print("Error: Image path or image-processing endpoint missing")
        sys.exit(1)

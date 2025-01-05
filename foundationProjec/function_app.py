import azure.functions as func
import datetime
import json
import logging
from azure.storage.blob import BlobServiceClient

import os
from dotenv import load_dotenv

from PIL import Image
from io import BytesIO

app = func.FunctionApp()

load_dotenv()


@app.blob_trigger(arg_name="myblob", path="images/{name}",
                               connection="AzureWebJobsStorage")
def BlobTrigger(myblob: func.InputStream):

    # Fetch the connection string from environment variables
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Connection string not found in environment variables.")

    if not connection_string:
        raise ValueError("Connection string not found in environment variables.")
    image_formats = ["jpeg", "jpg", "png"]

    logging.info(f"Python blob trigger function processed blob\n"
                f"Name: {myblob.name} "
                f"Blob Size: {myblob.__sizeof__()} bytes")

    logging.info(f"**********\n{myblob.name}")
    logging.info(f"**********\n{myblob.name.split(',')}")

    if myblob.name.split(".")[1].lower() in image_formats:
        try:
            image=Image.open(myblob)
            if image.mode in ("RGBA", "P"):  # RGBA or Palette-based images
                image = image.convert("RGB")  # Convert to RGB mode

            logging.info(f"Image Format: {image.format}, Image size: {image.size}")
            print("PROCESSING IMAGE ------------------")
            image.thumbnail(size=(100,150))         # thumbnail() converts the original image into a thumbnail


            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container="processed-images", blob=f"PROCESSED-{myblob.name}")


            image_buffer = BytesIO()
            image.save(image_buffer, format("JPEG"))
            image_buffer.seek(0)

            # uploading the processed image
            blob_client.upload_blob(image_buffer, overwrite=True)
            print(f"#################### {myblob.name.split('.')[0]} IMAGE PROCESSING COMPLETE ################")
        except Exception as e:
            logging.error(f"Failed to process image: {e}")



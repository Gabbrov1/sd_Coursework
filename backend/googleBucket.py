import os
from google.cloud import storage
from dotenv import load_dotenv


def get_bucket(bucketName):
    client = storage.Client()
    return client.bucket(bucketName)


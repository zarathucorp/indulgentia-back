from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, BlobClient
from env import AZURE_STORAGE_CONNECTION_STRING, DEFAULT_AZURE_CONTAINER_NAME, LOGS_AZURE_CONTAINER_NAME
from datetime import datetime, timedelta
from pydantic import UUID4
from func.error.error import raise_custom_error
import requests

azure_blob_client = BlobServiceClient.from_connection_string(
    conn_str=AZURE_STORAGE_CONNECTION_STRING)


def validate_url(url):
    response = requests.get(url)
    if response.status_code == 404:
        raise_custom_error(500, 312)
    else:
        print("URL is valid")


def generate_presigned_url(blob_name, container_name=DEFAULT_AZURE_CONTAINER_NAME, expiry_minutes=5):
    try:
        account_name = azure_blob_client.account_name
        blob_client = azure_blob_client.get_blob_client(
            container=container_name, blob=blob_name)

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=azure_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )

        blob_url = f"https://{account_name}.blob.core.windows.net/" + \
            f"{container_name}/{blob_name}?{sas_token}"
    except Exception as e:
        print(e)
        raise_custom_error(500, 312)

    validate_url(blob_url)
    return blob_url


def upload_blob(data: bytes, blob_name: str):
    try:
        blob_client = azure_blob_client.get_blob_client(
            container=DEFAULT_AZURE_CONTAINER_NAME, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 311)


def delete_blob(blob_name: str):
    try:
        blob_client = azure_blob_client.get_blob_client(
            container=DEFAULT_AZURE_CONTAINER_NAME, blob=blob_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 313)


def upload_logs_blob(data: bytes, blob_name: str):
    try:
        blob_client = azure_blob_client.get_blob_client(
            container=LOGS_AZURE_CONTAINER_NAME, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 311)

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from env import AZURE_STORAGE_CONNECTION_STRING, DEFAULT_AZURE_CONTAINER_NAME
from datetime import datetime, timedelta

azure_blob_client = BlobServiceClient.from_connection_string(
    conn_str=AZURE_STORAGE_CONNECTION_STRING)


def generate_presigned_url(blob_name, container_name=DEFAULT_AZURE_CONTAINER_NAME, expiry_minutes=5):
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
    return blob_url

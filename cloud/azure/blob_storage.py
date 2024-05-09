from azure.storage.blob import BlobServiceClient
from env import AZURE_STORAGE_CONNECTION_STRING

azure_client = BlobServiceClient.from_connection_string(
    conn_str=AZURE_STORAGE_CONNECTION_STRING)

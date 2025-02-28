from dotenv import load_dotenv
import os

load_dotenv()

current_mode = os.getenv("RUNNING_MODE")

if current_mode == "prod":
    AZURE_STORAGE_CONNECTION_STRING = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING")
    DEFAULT_AZURE_CONTAINER_NAME = os.getenv("DEFAULT_AZURE_CONTAINER_NAME")
    TOSS_PAYMENT_CLIENT_KEY = os.getenv("TOSS_PAYMENT_CLIENT_KEY")
    TOSS_PAYMENT_SECRET_KEY = os.getenv("TOSS_PAYMENT_SECRET_KEY")
elif current_mode == "dev":
    AZURE_STORAGE_CONNECTION_STRING = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING")
    DEFAULT_AZURE_CONTAINER_NAME = os.getenv("DEFAULT_AZURE_CONTAINER_NAME")
    TOSS_PAYMENT_CLIENT_KEY = os.getenv("TOSS_PAYMENT_CLIENT_KEY_TEST")
    TOSS_PAYMENT_SECRET_KEY = os.getenv("TOSS_PAYMENT_SECRET_KEY_TEST")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
AZURE_CONFIDENTIAL_LEDGER_NAME = os.getenv("AZURE_CONFIDENTIAL_LEDGER_NAME")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

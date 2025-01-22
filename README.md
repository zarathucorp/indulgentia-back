# indulgentia-back

> Server built with [FastAPI](https://fastapi.tiangolo.com/)

## Prerequisites
You will need the following information:
1. Basic Information
  - RUNNING_MODE: `RUNNING_MODE=prod` or `RUNNING_MODE=dev`
2. Supabase
  - SUPABASE_URL: Supabase URL
  - SUPABASE_KEY: Supabase secret key
3. Azure Blob Storage
  - AZURE_RESOURCE_GROUP
  - AZURE_STORAGE_CONNECTION_STRING
  - DEFAULT_AZURE_CONTAINER_NAME
  - AZURE_CONFIDENTIAL_LEDGER_NAME
  - AZURE_SUBSCRIPTION_ID
4. Azure Confidential Ledger
  - AZURE_CLIENT_ID
  - AZURE_TENANT_ID
  - AZURE_CLIENT_SECRET
4. Payment (Optional)
  - TOSS_PAYMENT_CLIENT_KEY_TEST: Used when `RUNNING_MODE=dev`
  - TOSS_PAYMENT_SECRET_KEY_TEST: Used when `RUNNING_MODE=dev`
  - TOSS_PAYMENT_CLIENT_KEY: Used when `RUNNING_MODE=prod`
  - TOSS_PAYMENT_SECRET_KEY: Used when `RUNNING_MODE=prod`

## Setup

```sh
git clone https://github.com/zarathucorp/indulgentia-back.git

# Set environment variables
cd indulgentia-back
touch .env

# Enter the environment variables from the prerequisites
(...)

```

## Learn More

**Documentation**: <a href="https://fastapi.tiangolo.com" target="_blank">https://fastapi.tiangolo.com</a>

**Source Code**: <a href="https://github.com/fastapi/fastapi" target="_blank">https://github.com/fastapi/fastapi</a>

## License

[MIT](LICENSE) (c) 2025 Zarathu Co.,Ltd
# indulgentia-back

> [FastAPI](https://fastapi.tiangolo.com/)로 구축된 Server

## 설정 전 준비사항
다음 정보가 필요합니다:
1. 기본사항
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
4. 결제(선택)
  - TOSS_PAYMENT_CLIENT_KEY_TEST: `RUNNING_MODE=dev`일 때 사용
  - TOSS_PAYMENT_SECRET_KEY_TEST: `RUNNING_MODE=dev`일 때 사용
  - TOSS_PAYMENT_CLIENT_KEY: `RUNNING_MODE=prod`일 때 사용
  - TOSS_PAYMENT_SECRET_KEY: `RUNNING_MODE=prod`일 때 사용

## 설정

```sh
git clone https://github.com/zarathucorp/indulgentia-back.git

# 환경변수 설정
cd indulgentia-back
touch .env

# 설정 전 준비사항 환경변수에 입력
(...)

```

## Learn More

**Documentation**: <a href="https://fastapi.tiangolo.com" target="_blank">https://fastapi.tiangolo.com</a>

**Source Code**: <a href="https://github.com/fastapi/fastapi" target="_blank">https://github.com/fastapi/fastapi</a>

## 라이선스

[MIT](LICENSE) (c) 2025 Zarathu Co.,Ltd
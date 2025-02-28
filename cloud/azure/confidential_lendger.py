import time
from azure.identity import DefaultAzureCredential

# import data plane sdk

from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient

# Set variables

from env import AZURE_CONFIDENTIAL_LEDGER_NAME
import json
from func.error.error import raise_custom_error


identity_url = "https://identity.confidential-ledger.core.azure.com"
ledger_url = "https://" + AZURE_CONFIDENTIAL_LEDGER_NAME + \
    ".confidential-ledger.azure.com"

# Authentication
credential = DefaultAzureCredential()

# Create a CL client
identity_client = ConfidentialLedgerCertificateClient(identity_url)
network_identity = identity_client.get_ledger_identity(
    ledger_id=AZURE_CONFIDENTIAL_LEDGER_NAME
)

ledger_tls_cert_file_name = f"cloud/azure/{AZURE_CONFIDENTIAL_LEDGER_NAME}.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity['ledgerTlsCertificate'])


ledger_client = ConfidentialLedgerClient(
    endpoint=ledger_url,
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)


def write_ledger(content: dict):
    '''
    Write to the ledger

    @param content: content to be written to the ledger
    -> timestamp 자동으로 생성됨. 따로 넣어 줄 필요 없음.
    '''
    print(AZURE_CONFIDENTIAL_LEDGER_NAME)
    entry = {"contents": json.dumps({**content, "timestamp": time.time()})}
    try:
        result = ledger_client.create_ledger_entry(entry=entry)
        return result
    except Exception as e:
        print(e)
        raise_custom_error(500, 321)


def read_ledger(transaction_id: str):
    '''
    Read from the ledger
    0.01초씩 딜레이 주는게 최선의 방법일지는 모르겠습니다.

    @param transaction_id: transaction id to read from the ledger
    '''
    try:
        status = ledger_client.get_transaction_status(
            transaction_id=transaction_id)
        if status.get("state") == "Pending":
            raise Exception("Transaction is still pending")
        elif status.get("state") != "Committed":
            raise Exception("Unknown Error - Transaction is not committed")
        time_spent = 0
        while True:
            entry = ledger_client.get_ledger_entry(
                transaction_id=transaction_id)
            if entry.get("state") == "Ready":
                return entry
            time.sleep(0.01)
            time_spent += 0.01

            if time_spent > 10:
                # raise Exception("Timeout")
                raise_custom_error(500, 323)

    except Exception as e:
        print(e)
        raise_custom_error(500, 322)

def get_ledger_receipt(transaction_id: str):
    '''
    Get the receipt of the transaction

    @param transaction_id: transaction id to get the receipt
    '''
    try:
        status = ledger_client.get_transaction_status(
            transaction_id=transaction_id)
        if status.get("state") == "Pending":
            raise Exception("Transaction is still pending")
        elif status.get("state") != "Committed":
            raise Exception("Unknown Error - Transaction is not committed")
        time_spent = 0
        while True:
            receipt = ledger_client.get_receipt(
                transaction_id=transaction_id)
            if receipt.get("state") == "Ready":
                return receipt
            time.sleep(0.01)
            time_spent += 0.01

            if time_spent > 10:
                # raise Exception("Timeout")
                raise_custom_error(500, 323)
    except Exception as e:
        print(e)
        raise_custom_error(500, 322)
        
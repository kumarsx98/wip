import time
import requests
import logging
import json
import os
import textwrap
from django.conf import settings
from django.core.files.storage import default_storage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants (replace these with your actual values)
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
API_KEY = "B1xJInq9KnjrEurPCS3N1K9I1KNyyvIh"
AUTH_TOKEN = "eyJqa3UiOiJodHRwOi8vZ3ByZC1hdXRoLmFiYnZpZW5ldC5jb206ODAxMC9zc28vYXV0aC5zZXJ2aWNlL2p3a3MiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJrc3N4MyIsImlzcyI6Imh0dHA6Ly9ncHJkLWF1dGguYWJidmllbmV0LmNvbSIsImV4cCI6MTcxNTcwNTYwMywiZW1haWwiOiJzYWNoaW4ua3NAYWJidmllLmNvbSIsImZuIjoiS3MsIFNhY2hpbiIsInVwaSI6IjE1MTE5NDgxIiwiZG9tYWluIjoiQUJCVklFTkVUIiwicm9sZXMiOltdfQ.BpVkKD1HgxkUA_OysK7KhyjVERcyr8H5EDimkhpHhb_2lWsoDwhNq_lqw4gkmEYm-6HTPD0ZK_LTpBCUyDMd5ipbZX5VusEvlRFn2E5D-ovafG9kxPCXXoj6A9oNQ7VfHwMA7g6b7zzwRjEc23tjuhnDQCcnhMXNHln0ye8kRVE"


def get_api_headers():
    headers = {
        "x-api-key": API_KEY,
        "x-user-token": AUTH_TOKEN,
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    print(f"Generated headers: {json.dumps(headers, indent=4)}")
    return headers


def delete_existing_document(source, filename):
    try:
        headers = get_api_headers()
        documents = get_documents_from_iliad(source)
        for doc in documents:
            if doc.get('filename') == filename:
                doc_id = doc.get('id')
                delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{doc_id}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 204:
                    logger.info(f"Document '{filename}' deleted successfully from source '{source}'.")
                else:
                    logger.warning(
                        f"Failed to delete document '{filename}' from source '{source}'. Status: {response.status_code}, Response: {response.text}")
                break
    except requests.RequestException as e:
        logger.error(f"Error deleting document '{filename}': {str(e)}")


def upload_document_to_iliad(source, file):
    try:
        headers = get_api_headers()
        url = f"{ILIAD_URL}/api/v1/sources/{source.lower()}/documents"

        # Replace document if it exists
        delete_existing_document(source, file.name)

        files = {"file": (file.name, file, 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()

        response_json = response.json()
        if response.status_code in [200, 201, 202]:
            task_id = response_json.get('task_id')
            document_id = response_json.get('document_id')
            return {"status": "success", "task_id": task_id, "document_id": document_id}
        else:
            return {"status": "error", "message": f"API error: {response.text}"}

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def check_upload_status(source, task_id, max_retries=3, delay=10):
    for attempt in range(max_retries):
        try:
            headers = get_api_headers()
            url = f"{ILIAD_URL}/api/v1/sources/{source}/{task_id}"
            print(f"Checking upload status: URL: {url}, Task ID: {task_id}, Attempt: {attempt + 1}")

            response = requests.get(url, headers=headers)
            print(
                f"Upload status response: Status {response.status_code}, Content: {json.dumps(response.json(), indent=4)}")

            if response.status_code == 200:
                status_data = response.json()
                return {
                    "status": status_data.get('status', 'UNKNOWN'),
                    "message": f"Upload status: {status_data.get('status', 'UNKNOWN')}",
                    "full_response": status_data
                }
            else:
                print(f"Error checking upload status. Status code: {response.status_code}")
                return {
                    "status": "ERROR",
                    "message": f"Error checking status: {response.text}",
                    "full_response": {"error": response.text}
                }

        except requests.RequestException as e:
            print(f"Error checking upload status: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "full_response": {"error": str(e)}
            }

        time.sleep(delay)

    return {
        "status": "PENDING",
        "message": "Upload is still in progress. Please check back later.",
        "full_response": {"status": "PENDING"}
    }


def get_sources_from_iliad():
    try:
        headers = get_api_headers()
        url = f"{ILIAD_URL}/api/v1/sources"
        print(f"Fetching sources from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sources_data = response.json()

        print(f"Iliad API response for sources: {json.dumps(sources_data, indent=4)}")

        all_sources = []
        if isinstance(sources_data, dict):
            all_sources.extend(sources_data.get('global_sources', []))
            all_sources.extend(sources_data.get('private_sources', []))
        else:
            print(f"Unexpected response format from Iliad API: {json.dumps(sources_data, indent=4)}")

        print(f"All sources: {json.dumps(all_sources, indent=4)}")
        return all_sources
    except requests.RequestException as e:
        print(f"Error fetching sources from Iliad API: {str(e)}")
        return []


def get_documents_from_iliad(source):
    try:
        headers = get_api_headers()
        url = f"{ILIAD_URL}/api/v1/sources/{source}/documents"
        print(f"Fetching documents from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        documents_data = response.json()

        print(f"Iliad API response for documents: {json.dumps(documents_data, indent=4)}")

        return documents_data.get('documents', [])
    except requests.RequestException as e:
        print(f"Error fetching documents from Iliad API: {str(e)}")
        return []


def upload_and_verify(source, file):
    upload_result = upload_document_to_iliad(source, file)
    if upload_result['status'] == 'success':
        task_id = upload_result['task_id']
        document_id = upload_result.get('document_id')

        # Wait for the upload to complete
        for _ in range(5):  # Try 5 times
            time.sleep(5)  # Wait 5 seconds between checks
            status = check_upload_status(source, task_id)
            if status['status'] == 'SUCCESS':
                print("Upload completed successfully")
                break
            print(f"Upload status: {status['status']}")

        # Wait a bit more before listing documents
        print("Waiting 10 seconds before fetching document list...")
        time.sleep(10)

        # List documents and check for the new one
        documents = get_documents_from_iliad(source)
        print(f"Retrieved {len(documents)} documents from the source")

        new_doc = next((doc for doc in documents if doc.get('id') == document_id), None)

        if new_doc:
            print(f"Document successfully uploaded and visible: {json.dumps(new_doc, indent=4)}")
        else:
            print(f"Document uploaded but not visible in the list. Document ID: {document_id}")
            print("List of document IDs retrieved:")
            for doc in documents:
                print(f"- {doc.get('id')}: {doc.get('name', 'No name')}")
    else:
        print("Upload failed")

    return upload_result

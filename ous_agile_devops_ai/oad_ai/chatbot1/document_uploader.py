import time
import requests
import logging
import json
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.files.storage import default_storage
import os
import shutil
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants and decryption for sensitive information
ENCRYPTION_KEY = settings.ENCRYPTION_KEY
ENCRYPTED_API_KEY = settings.ENCRYPTED_API_KEY
AUTH_TOKEN = settings.AUTH_TOKEN

# Decrypt the API key
fernet = Fernet(ENCRYPTION_KEY.encode())
API_KEY = fernet.decrypt(ENCRYPTED_API_KEY.encode()).decode()

# Setting the ILIAD URL
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"


def get_api_headers():
    headers = {
        "x-api-key": API_KEY,
        "x-user-token": AUTH_TOKEN,
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    logger.info(f"Generated headers: {json.dumps(headers, indent=4)}")
    return headers


def delete_existing_document(source, document_id):
    try:
        headers = get_api_headers()
        delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{document_id}"
        response = requests.delete(delete_url, headers=headers)
        if response.status_code == 204:
            logger.info(f"Document '{document_id}' deleted successfully from source '{source}'.")
        else:
            logger.warning(
                f"Failed to delete document '{document_id}' from source '{source}'. Status: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error deleting document '{document_id}': {str(e)}")


def save_file_for_preview(source, file):
    filename = file.name
    # Remove the source name before the file name
    clean_filename = filename.split('#', 1)[-1]

    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)

    new_file_path = os.path.join(preview_dir, clean_filename)

    with default_storage.open(new_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # Construct preview URL using the correct pattern
    encoded_filename = urllib.parse.quote(clean_filename)
    preview_url = f"{settings.MEDIA_URL}previews/{encoded_filename}"

    logger.info(f"Saved file for preview: {new_file_path}, URL: {preview_url}")
    return preview_url


def upload_document_to_iliad(source, file):
    try:
        headers = get_api_headers()
        url = f"{ILIAD_URL}/api/v1/sources/{source.lower()}/documents"

        # Replace document if it exists
        documents = get_documents_from_iliad(source)
        for doc in documents:
            if doc.get('filename') == file.name:
                delete_existing_document(source, doc.get('id'))

        files = {"file": (file.name, file, 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()

        response_json = response.json()
        if response.status_code in [200, 201, 202]:
            task_id = response_json.get('task_id')
            document_id = response_json.get('document_id')

            # Save file locally and construct preview URL
            preview_url = save_file_for_preview(source, file)

            return {"status": "success", "task_id": task_id, "document_id": document_id, "preview_url": preview_url}
        else:
            return {"status": "error", "message": f"API error: {response.text}"}

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def check_upload_status(source, task_id, max_retries=3, delay=10):
    for attempt in range(max_retries):
        try:
            headers = get_api_headers()
            url = f"{ILIAD_URL}/api/v1/sources/{source}/{task_id}"
            logger.info(f"Checking upload status: URL: {url}, Task ID: {task_id}, Attempt: {attempt + 1}")

            response = requests.get(url, headers=headers)
            logger.info(
                f"Upload status response: Status {response.status_code}, Content: {json.dumps(response.json(), indent=4)}")

            if response.status_code == 200:
                status_data = response.json()
                return {
                    "status": status_data.get('status', 'UNKNOWN'),
                    "message": f"Upload status: {status_data.get('status', 'UNKNOWN')}",
                    "full_response": status_data
                }
            else:
                logger.warning(f"Error checking upload status. Status code: {response.status_code}")
                return {
                    "status": "ERROR",
                    "message": f"Error checking status: {response.text}",
                    "full_response": {"error": response.text}
                }

        except requests.RequestException as e:
            logger.error(f"Error checking upload status: {str(e)}")
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
        logger.info(f"Fetching sources from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sources_data = response.json()

        logger.info(f"Iliad API response for sources: {json.dumps(sources_data, indent=4)}")

        all_sources = []
        if isinstance(sources_data, dict):
            all_sources.extend(sources_data.get('global_sources', []))
            all_sources.extend(sources_data.get('private_sources', []))
        else:
            logger.warning(f"Unexpected response format from Iliad API: {json.dumps(sources_data, indent=4)}")

        logger.info(f"All sources: {json.dumps(all_sources, indent=4)}")
        return all_sources
    except requests.RequestException as e:
        logger.error(f"Error fetching sources from Iliad API: {str(e)}")
        return []


def get_documents_from_iliad(source):
    try:
        headers = get_api_headers()
        url = f"{ILIAD_URL}/api/v1/sources/{source}/documents"
        logger.info(f"Fetching documents from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        documents_data = response.json()

        logger.info(f"Iliad API response for documents: {json.dumps(documents_data, indent=4)}")

        return documents_data.get('documents', [])
    except requests.RequestException as e:
        logger.error(f"Error fetching documents from Iliad API: {str(e)}")
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
                logger.info("Upload completed successfully")
                break
            logger.info(f"Upload status: {status['status']}")

        # Wait a bit more before listing documents
        logger.info("Waiting 10 seconds before fetching document list...")
        time.sleep(10)

        # List documents and check for the new one
        documents = get_documents_from_iliad(source)
        logger.info(f"Retrieved {len(documents)} documents from the source")

        new_doc = next((doc for doc in documents if doc.get('id') == document_id), None)

        if new_doc:
            logger.info(f"Document successfully uploaded and visible: {json.dumps(new_doc, indent=4)}")
        else:
            logger.warning(f"Document uploaded but not visible in the list. Document ID: {document_id}")
            logger.info("List of document IDs retrieved:")
            for doc in documents:
                logger.info(f"- {doc.get('id')}: {doc.get('name', 'No name')}")
    else:
        logger.warning("Upload failed")

    return upload_result

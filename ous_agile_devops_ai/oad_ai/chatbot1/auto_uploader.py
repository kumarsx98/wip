import os
import time
import shutil
import logging

import schedule
from django.conf import settings
from cryptography.fernet import Fernet
import requests
from .models import UploadRecord

logger = logging.getLogger(__name__)

ILIAD_URL = settings.ILIAD_URL

def get_headers():
    try:
        encryption_key = settings.ENCRYPTION_KEY.encode()
        encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
        cipher_suite = Fernet(encryption_key)
        api_key = cipher_suite.decrypt(encrypted_api_key).decode()

        headers = {
            "x-api-key": api_key,
            "x-user-token": settings.AUTH_TOKEN,
            "Authorization": f"Bearer {settings.AUTH_TOKEN}"
        }
        logger.info(f"Generated headers: {headers}")
        return headers
    except Exception as e:
        logger.error(f"Error creating headers: {str(e)}")
        return None

def get_sources_from_iliad():
    try:
        headers = get_headers()
        if not headers:
            return []

        url = f"{ILIAD_URL}/api/v1/sources"
        logger.info(f"Fetching sources from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sources_data = response.json()

        logger.info(f"Iliad API response for sources: {sources_data}")

        all_sources = []
        if isinstance(sources_data, dict):
            all_sources.extend(sources_data.get('global_sources', []))
            all_sources.extend(sources_data.get('private_sources', []))
        else:
            logger.error(f"Unexpected response format from Iliad API: {sources_data}")

        logger.info(f"All sources: {all_sources}")
        return [source.lower() for source in all_sources]
    except requests.RequestException as e:
        logger.error(f"Error fetching sources from Iliad API: {e}")
        return []

def get_documents_from_iliad(source):
    try:
        headers = get_headers()
        if not headers:
            return []

        url = f"{ILIAD_URL}/api/v1/sources/{source}/documents"
        logger.info(f"Fetching documents from Iliad API: URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        documents_data = response.json()

        logger.info(f"Iliad API response for documents: {documents_data}")

        return documents_data.get('documents', [])
    except requests.RequestException as e:
        logger.error(f"Error fetching documents from Iliad API: {str(e)}")
        return []

def delete_existing_document(source, filename):
    try:
        headers = get_headers()
        if not headers:
            return False

        documents = get_documents_from_iliad(source)
        for doc in documents:
            if doc.get('filename') == filename:
                doc_id = doc.get('id')
                delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{doc_id}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 204:
                    logger.info(f"Document '{filename}' deleted successfully from source '{source}'.")
                    return True
                else:
                    logger.warning(f"Failed to delete document '{filename}' from source '{source}'. Status: {response.status_code}, Response: {response.text}")
                    return False
        logger.info(f"Document '{filename}' not found in source '{source}'.")
        return True
    except requests.RequestException as e:
        logger.error(f"Error deleting document '{filename}': {str(e)}")
        return False

def upload_document_to_iliad(source, file_path):
    try:
        headers = get_headers()
        if not headers:
            return None

        filename = os.path.basename(file_path)

        # Delete existing document if it exists
        if not delete_existing_document(source, filename):
            logger.error(f"Failed to delete existing document '{filename}' from source '{source}'.")
            return None

        with open(file_path, 'rb') as file:
            url = f"{ILIAD_URL}/api/v1/sources/{source.lower()}/documents"
            files = {"file": (filename, file, 'application/octet-stream')}

            logger.info(f"Sending request to Iliad API: URL: {url}, Headers: {headers}, File: {filename}")

            file.seek(0)
            logger.info(f"First 100 bytes of file {file_path}: {file.read(100)}")
            file.seek(0)

            response = requests.post(url, headers=headers, files=files)

        logger.info(f"Iliad API response for {file_path}: Status {response.status_code}, Content: {response.text}")

        if response.status_code in [200, 201, 202]:
            response_json = response.json()
            task_id = response_json.get('task_id')
            if task_id:
                logger.info(f"Received task ID: {task_id}")
                return {"status": "PENDING", "task_id": task_id}
            else:
                logger.info("No task ID received, but upload seems successful")
                return {"status": "COMPLETED", "message": "Upload successful"}
        else:
            logger.error(f"Error uploading document to Iliad API. Status code: {response.status_code}")
            return None

    except requests.RequestException as e:
        logger.error(f"Error uploading document to Iliad API: {str(e)}")
        return None

def check_upload_status(source, task_id):
    try:
        headers = get_headers()
        if not headers:
            return None

        url = f"{ILIAD_URL}/api/v1/sources/{source}/{task_id}"
        logger.info(f"Checking upload status: URL: {url}, Task ID: {task_id}")

        response = requests.get(url, headers=headers)
        logger.info(f"Upload status response: Status {response.status_code}, Content: {response.text}")

        if response.status_code == 200:
            status_data = response.json()
            if status_data.get('status') in ['COMPLETED', 'SUCCESS']:
                return {'status': 'COMPLETED'}
            return status_data
        elif response.status_code == 404:
            logger.warning(f"Task ID: {task_id}. Assuming upload was successful.")
            return {"status": "COMPLETED", "message": "Assuming upload was successful"}
        else:
            logger.error(f"Error checking upload status. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error checking upload status: {str(e)}")
        return None

def get_source_from_filename(filename, sources):
    parts = filename.split('-')
    logger.info(f"Filename parts: {parts}")
    logger.info(f"Available sources: {sources}")

    for i in range(1, len(parts) + 1):
        potential_source = '-'.join(parts[:i]).lower()
        logger.info(f"Checking potential source: {potential_source}")
        if potential_source in sources:
            logger.info(f"Source found: {potential_source}")
            return potential_source

    logger.warning(f"No matching source found for filename: {filename}")
    return None

def process_documents():
    auto_upload_dir = os.path.join(settings.MEDIA_ROOT, 'auto_upload')
    manual_check_dir = os.path.join(settings.MEDIA_ROOT, 'manual_check')

    # Ensure the auto_upload directory exists
    if not os.path.exists(auto_upload_dir):
        os.makedirs(auto_upload_dir)
        logger.info(f"Created auto_upload directory: {auto_upload_dir}")

    logger.info(f"Auto upload directory: {auto_upload_dir}")
    logger.info(f"Manual check directory: {manual_check_dir}")

    sources = get_sources_from_iliad()
    logger.info(f"Retrieved sources from Iliad: {sources}")

    if not sources:
        logger.error("No sources available. Skipping document processing.")
        return {"processed_files": [], "unprocessed_files": []}

    processed_files = []
    unprocessed_files = []

    try:
        files_in_directory = os.listdir(auto_upload_dir)
        logger.info(f"Files in auto_upload directory: {files_in_directory}")

        for filename in files_in_directory:
            file_path = os.path.join(auto_upload_dir, filename)
            logger.info(f"Processing file: {filename}")

            if not os.path.isfile(file_path):
                logger.warning(f"Skipping non-file item: {filename}")
                unprocessed_files.append({"file_name": filename, "reason": "Not a file"})
                continue

            # Check file extension
            _, file_extension = os.path.splitext(filename)
            if file_extension.lower() in ['.docx', '.doc']:
                logger.warning(f"Unsupported file type: {file_extension}. Moving to manual check folder.")
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                logger.info(f"Moved {filename} to manual check folder")
                UploadRecord.objects.create(
                    file_name=filename,
                    source='UNKNOWN',
                    status='UNSUPPORTED_FILE_TYPE'
                )
                unprocessed_files.append({"file_name": filename, "reason": "Unsupported file type"})
                continue

            source = get_source_from_filename(filename, sources)
            logger.info(f"Detected source for {filename}: {source}")

            if not source:
                logger.warning(f"No source found for filename: {filename}. Moving to manual check folder.")
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                logger.info(f"Moved {filename} to manual check folder")
                UploadRecord.objects.create(
                    file_name=filename,
                    source='UNKNOWN',
                    status='NO_SOURCE_FOUND'
                )
                unprocessed_files.append({"file_name": filename, "reason": "No source found"})
                continue

            upload_result = upload_document_to_iliad(source, file_path)
            logger.info(f"Upload result for {filename}: {upload_result}")

            if not upload_result:
                logger.error(f"Failed to upload {filename} to Iliad API. Moving to manual check folder.")
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                logger.info(f"Moved {filename} to manual check folder")
                UploadRecord.objects.create(
                    file_name=filename,
                    source=source,
                    status='UPLOAD_FAILED'
                )
                unprocessed_files.append({"file_name": filename, "reason": "Upload failed"})
                continue

            status = upload_result.get('status', 'UNKNOWN')
            task_id = upload_result.get('task_id')

            UploadRecord.objects.create(
                file_name=filename,
                source=source,
                status=status,
                task_id=task_id
            )
            logger.info(f"Created UploadRecord for {filename}")

            if status == 'PENDING' and task_id:
                max_retries = 5
                retry_delay = 30  # seconds
                for attempt in range(max_retries):
                    time.sleep(retry_delay)
                    upload_status = check_upload_status(source, task_id)
                    if upload_status and upload_status.get('status') in ['COMPLETED', 'SUCCESS']:
                        processed_files.append({"file_name": filename, "status": "COMPLETED"})
                        logger.info(f"File {filename} uploaded successfully to Iliad API after {attempt + 1} attempts.")
                        os.remove(file_path)
                        logger.info(f"Removed {filename} from auto_upload directory")
                        UploadRecord.objects.filter(file_name=filename).update(status='COMPLETED')
                        break
                    elif upload_status and upload_status.get('status') == 'FAILED':
                        unprocessed_files.append({"file_name": filename, "reason": "Upload failed"})
                        logger.error(f"Upload failed for {filename} after {attempt + 1} attempts.")
                        shutil.move(file_path, os.path.join(manual_check_dir, filename))
                        logger.info(f"Moved {filename} to manual check folder")
                        UploadRecord.objects.filter(file_name=filename).update(status='UPLOAD_FAILED')
                        break
                else:
                    unprocessed_files.append({"file_name": filename, "reason": "Max retries reached"})

    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")

    return {"processed_files": processed_files, "unprocessed_files": unprocessed_files}

def scheduled_process():
    try:
        logger.info("Running scheduled document processing")
        processed_files = process_documents()
        if not processed_files:
            return {"status": "success", "message": "No files processed."}

        return {"status": "success", "processed": processed_files}
    except Exception as e:
        logger.error(f"Error in scheduled process: {str(e)}")
        return {"status": "error", "message": str(e)}

def start_scheduler():
    schedule.every(10).minutes.do(scheduled_process)  # Adjust the schedule as needed
    logger.info("Scheduler started for auto-upload process")
    while True:
        schedule.run_pending()
        time.sleep(1)

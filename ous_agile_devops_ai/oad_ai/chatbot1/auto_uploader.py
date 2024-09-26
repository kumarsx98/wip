#autouploader.py

import os
import shutil
import logging
import time
import schedule
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from cryptography.fernet import Fernet
from .models import UploadRecord
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

ILIAD_URL = settings.ILIAD_URL
PREVIEW_BASE_URL = settings.PREVIEW_BASE_URL


def get_headers():
    try:
        encryption_key = settings.ENCRYPTION_KEY.encode()
        encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
        cipher_suite = Fernet(encryption_key)
        api_key = cipher_suite.decrypt(encrypted_api_key).decode()

        headers = {
            "x-api-key": api_key,
            "Authorization": f"Bearer {settings.AUTH_TOKEN}"
        }
        return headers
    except Exception as e:
        logger.error(f"Error creating headers: {str(e)}")
        return None


def get_sources_from_iliad():
    headers = get_headers()
    if not headers:
        return []

    url = f"{ILIAD_URL}/api/v1/sources"
    response = requests.get(url, headers=headers)
    sources_data = response.json()
    all_sources = []
    if isinstance(sources_data, dict):
        all_sources.extend(sources_data.get('global_sources', []))
        all_sources.extend(sources_data.get('private_sources', []))
    return [source.lower() for source in all_sources]


def get_documents_from_iliad(source):
    headers = get_headers()
    if not headers:
        return []

    url = f"{ILIAD_URL}/api/v1/sources/{source}/documents"
    response = requests.get(url, headers=headers)
    documents_data = response.json()
    return documents_data.get('documents', [])


def delete_existing_document(source, filename):
    headers = get_headers()
    if not headers:
        return False

    documents = get_documents_from_iliad(source)
    for doc in documents:
        if doc.get('filename') == filename:
            doc_id = doc.get('id')
            delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{doc_id}"
            response = requests.delete(delete_url, headers=headers)
            return response.status_code == 204
    return False


import urllib.parse


def save_file_for_preview(file_path):
    filename = os.path.basename(file_path)
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)
    new_file_path = os.path.join(preview_dir, filename)
    shutil.copy(file_path, new_file_path)
    return f"{PREVIEW_BASE_URL}/media/previews/{urllib.parse.quote(filename)}"


def upload_document_to_iliad(source, file_path):
    headers = get_headers()
    if not headers:
        return None

    filename = os.path.basename(file_path)
    delete_existing_document(source, filename)
    preview_url = save_file_for_preview(file_path)

    with open(file_path, 'rb') as file:
        url = f"{ILIAD_URL}/api/v1/sources/{source.lower()}/documents"
        files = {"file": (filename, file, 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201, 202]:
        response_json = response.json()
        task_id = response_json.get('task_id', None)
        return {
            "status": "COMPLETED" if not task_id else "PENDING",
            "task_id": task_id,
            "preview_url": preview_url,
        }
    return None


def check_upload_status(source, task_id):
    headers = get_headers()
    if not headers:
        return None

    url = f"{ILIAD_URL}/api/v1/sources/{source}/{task_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        status_data = response.json()
        return status_data.get('status', 'FAILED') in ['COMPLETED', 'SUCCESS']
    return False


def get_source_from_filename(filename, sources):
    parts = filename.split('#')
    for i in range(1, len(parts) + 1):
        potential_source = '-'.join(parts[:i]).lower()
        if potential_source in sources:
            return potential_source
    return None


def process_documents():
    auto_upload_dir = os.path.join(settings.MEDIA_ROOT, 'auto_upload')
    manual_check_dir = os.path.join(settings.MEDIA_ROOT, 'manual_check')
    if not os.path.exists(auto_upload_dir):
        os.makedirs(auto_upload_dir)

    sources = get_sources_from_iliad()
    processed_files = []
    unprocessed_files = []

    try:
        files_in_directory = os.listdir(auto_upload_dir)
        for filename in files_in_directory:
            file_path = os.path.join(auto_upload_dir, filename)
            if not os.path.isfile(file_path):
                unprocessed_files.append({"file_name": filename, "reason": "Not a file"})
                continue
            _, file_extension = os.path.splitext(filename)
            if file_extension.lower() in ['.docx', '.doc']:
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                UploadRecord.objects.create(file_name=filename, source='UNKNOWN', status='UNSUPPORTED_FILE_TYPE')
                unprocessed_files.append({"file_name": filename, "reason": "Unsupported file type"})
                continue
            source = get_source_from_filename(filename, sources)
            if not source:
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                UploadRecord.objects.create(file_name=filename, source='UNKNOWN', status='NO_SOURCE_FOUND')
                unprocessed_files.append({"file_name": filename, "reason": "No source found"})
                continue
            upload_result = upload_document_to_iliad(source, file_path)
            if not upload_result:
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                UploadRecord.objects.create(file_name=filename, source=source, status='UPLOAD_FAILED')
                unprocessed_files.append({"file_name": filename, "reason": "Upload failed"})
                continue
            status = upload_result.get('status', 'UNKNOWN')
            task_id = upload_result.get('task_id')
            preview_url = upload_result.get('preview_url', '')
            UploadRecord.objects.create(file_name=filename, source=source, status=status, task_id=task_id,
                                        preview_url=preview_url)
            if status == 'PENDING' and task_id:
                for attempt in range(5):
                    time.sleep(30)
                    if check_upload_status(source, task_id):
                        os.remove(file_path)
                        UploadRecord.objects.filter(file_name=filename).update(status='COMPLETED')
                        processed_files.append({
                            "file_name": filename,
                            "status": "COMPLETED",
                            "preview_url": preview_url,
                            "task_id": task_id
                        })
                        break
                else:
                    unprocessed_files.append({"file_name": filename, "reason": "Max retries reached"})
            else:
                processed_files.append({
                    "file_name": filename,
                    "status": status,
                    "preview_url": preview_url,
                    "task_id": task_id
                })
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
    return {"processed_files": processed_files, "unprocessed_files": unprocessed_files}


def get_previews():
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)
    return [os.path.join(preview_dir, f) for f in os.listdir(preview_dir) if
            os.path.isfile(os.path.join(preview_dir, f))]


def get_upload_status(request):
    upload_records = UploadRecord.objects.all().values('file_name', 'source', 'status', 'task_id', 'timestamp',
                                                       'preview_url')
    upload_details = list(upload_records)
    previews = get_previews()

    existing_files = set(record['file_name'] for record in upload_details)

    for preview in previews:
        file_name = os.path.basename(preview)
        if file_name not in existing_files:
            upload_details.append({
                "file_name": file_name,
                "status": "NOT UPLOADED",
                "task_id": None,
                "timestamp": None,
                "preview_url": f"{PREVIEW_BASE_URL}/media/previews/{urllib.parse.quote(file_name)}"
            })

    response = {
        "status": "success",
        "scheduler_status": get_scheduler_status(),  # Modify this to get the actual scheduler status if needed
        "upload_details": upload_details
    }
    return JsonResponse(response)


def get_scheduler_status():
    # Implement this function to return the scheduler status
    return "Not running"


def start_scheduler():
    schedule.every(10).minutes.do(process_documents)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Example of starting the scheduler
if __name__ == "__main__":
    start_scheduler()

import os
import time
import shutil
import logging
import urllib.parse

import schedule
from django.conf import settings
from cryptography.fernet import Fernet
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import UploadRecord

logger = logging.getLogger(__name__)

ILIAD_URL = settings.ILIAD_URL
PREVIEW_BASE_URL = settings.PREVIEW_BASE_URL  # URL base for preview


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


def save_file_for_preview(file_path, source):
    try:
        filename = os.path.basename(file_path)
        # Create a clean filename that matches the working pattern
        clean_filename = f"{source}#{filename}"

        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)

        new_file_path = os.path.join(preview_dir, clean_filename)
        shutil.copy(file_path, new_file_path)

        # Construct preview URL using the correct pattern
        encoded_filename = urllib.parse.quote(clean_filename)
        preview_url = f"{PREVIEW_BASE_URL}/media/previews/{encoded_filename}"

        logger.info(f"Saved file for preview: {new_file_path}, URL: {preview_url}")
        return preview_url
    except Exception as e:
        logger.error(f"Error saving file for preview: {str(e)}")
        return None


def upload_document_to_iliad(source, file_path):
    try:
        headers = get_headers()
        if not headers:
            return None

        filename = os.path.basename(file_path)
        logger.info(f"API Called'{filename}'")

        if not delete_existing_document(source, filename):
            logger.error(f"Failed to delete existing document '{filename}' from source '{source}'.")
            return None

        # Save file for preview with the correct source prefix
        preview_url = save_file_for_preview(file_path, source.lower())

        with open(file_path, 'rb') as file:
            url = f"{ILIAD_URL}/api/v1/sources/{source.lower()}/documents"
            files = {"file": (filename, file, 'application/octet-stream')}

            logger.info(f"Sending request to Iliad API: URL: {url}, Headers: {headers}, File: {filename}")
            response = requests.post(url, headers=headers, files=files)

        logger.info(f"Iliad API response for {file_path}: Status {response.status_code}, Content: {response.text}")

        if response.status_code in [200, 201, 202]:
            response_json = response.json()
            task_id = response_json.get('task_id')
            return {
                "status": "PENDING" if task_id else "COMPLETED",
                "task_id": task_id,
                "preview_url": preview_url,
                "message": "Upload successful"
            }
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
        logger.info(f"Checking status for task {task_id} in source {source}")

        response = requests.get(url, headers=headers)
        logger.info(f"Status check response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            status_data = response.json()
            current_status = status_data.get('status', '').upper()

            if current_status in ['COMPLETED', 'SUCCESS']:
                UploadRecord.objects.filter(task_id=task_id).update(status='COMPLETED')
                return {'status': 'COMPLETED'}
            elif current_status == 'FAILED':
                UploadRecord.objects.filter(task_id=task_id).update(status='FAILED')
                return {'status': 'FAILED'}
            else:
                return {'status': 'PENDING'}
        elif response.status_code == 404:
            UploadRecord.objects.filter(task_id=task_id).update(status='COMPLETED')
            return {"status": "COMPLETED"}
        else:
            logger.error(f"Error checking upload status. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error checking upload status: {str(e)}")
        return None


def get_upload_records():
    try:
        records = UploadRecord.objects.all().order_by('-timestamp')[:50]
        updated_records = []

        for record in records:
            if record.status == 'PENDING' and record.task_id:
                status_result = check_upload_status(record.source, record.task_id)
                if status_result and status_result['status'] != 'PENDING':
                    record.status = status_result['status']
                    record.save()

            # Construct the preview URL using the correct pattern
            preview_url = None
            if record.preview_url:
                filename = f"{record.source}#{os.path.basename(record.file_name)}"
                encoded_filename = urllib.parse.quote(filename)
                preview_url = f"{PREVIEW_BASE_URL}/media/previews/{encoded_filename}"

            updated_records.append({
                "file_name": record.file_name,
                "source": record.source,
                "status": record.status,
                "task_id": record.task_id,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "preview_url": preview_url
            })

        return updated_records
    except Exception as e:
        logger.error(f"Error fetching upload records: {str(e)}")
        return []


@api_view(['GET'])
def get_upload_status(request):
    try:
        records = get_upload_records()

        completed_files = sum(1 for record in records if record['status'] == 'COMPLETED')

        return Response({
            "status": "success",
            "upload_details": records,
            "processed_files": completed_files
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)


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
        logger.info(f"Created auto_upload directory: {auto_upload_dir}")

    sources = get_sources_from_iliad()
    if not sources:
        logger.error("No sources available. Skipping document processing.")
        return {"processed_files": [], "unprocessed_files": []}

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
                UploadRecord.objects.create(
                    file_name=filename,
                    source='UNKNOWN',
                    status='UNSUPPORTED_FILE_TYPE'
                )
                unprocessed_files.append({"file_name": filename, "reason": "Unsupported file type"})
                continue

            source = get_source_from_filename(filename, sources)

            if not source:
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                UploadRecord.objects.create(
                    file_name=filename,
                    source='UNKNOWN',
                    status='NO_SOURCE_FOUND'
                )
                unprocessed_files.append({"file_name": filename, "reason": "No source found"})
                continue

            upload_result = upload_document_to_iliad(source, file_path)

            if upload_result:
                status = upload_result.get('status', 'PENDING')
                task_id = upload_result.get('task_id')
                preview_url = upload_result.get('preview_url')

                record = UploadRecord.objects.create(
                    file_name=filename,
                    source=source,
                    status=status,
                    task_id=task_id,
                    preview_url=preview_url
                )
                if task_id:
                    status_result = check_upload_status(source, task_id)
                    if status_result and status_result['status'] != 'PENDING':
                        record.status = status_result['status']
                        record.save()

                processed_files.append({
                    "file_name": filename,
                    "source": source,
                    "status": record.status,
                    "task_id": task_id,
                    "preview_url": preview_url
                })
                os.remove(file_path)
            else:
                shutil.move(file_path, os.path.join(manual_check_dir, filename))
                UploadRecord.objects.create(
                    file_name=filename,
                    source=source,
                    status='FAILED'
                )
                unprocessed_files.append({"file_name": filename, "reason": "Upload failed"})

        return {
            "processed_files": processed_files,
            "unprocessed_files": unprocessed_files
        }

    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        return {
            "error": str(e),
            "processed_files": processed_files,
            "unprocessed_files": unprocessed_files
        }



# views.py

import json
#from wsgiref.validate import check_status

from .auto_uploader import process_documents, get_upload_records
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
import concurrent.futures
import datetime
import traceback
from cryptography.fernet import Fernet
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .models import Source  # Make sure to import your Source model
import urllib.parse
from .document_uploader import upload_document_to_iliad, check_upload_status
import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from djangosaml2 import views as saml_views
from djangosaml2.conf import get_config
from django.contrib.auth.models import User



logger = logging.getLogger(__name__)

scheduler_thread = None
scheduler_running = False
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
PREVIEW_BASE_URL = settings.PREVIEW_BASE_URL




AUTO_UPLOAD_DIRECTORY = settings.AUTO_UPLOAD_DIR

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .document_uploader import upload_document_to_iliad, check_upload_status as check_status


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def check_status(source, task_id):
    # implement your status check logic here
    # this dummy implementation returns a fake status
    return {
        'status': 'SUCCESS',
        'message': 'Task completed successfully',
        'full_response': {}
    }


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from cryptography.fernet import Fernet
import requests


# Helper function to generate headers
def get_api_headers():
    encryption_key = settings.ENCRYPTION_KEY.encode()
    encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
    cipher_suite = Fernet(encryption_key)
    api_key = cipher_suite.decrypt(encrypted_api_key).decode()
    headers = {
        "x-api-key": api_key,
        "x-user-token": settings.AUTH_TOKEN,
        "Authorization": f"Bearer {settings.AUTH_TOKEN}"
    }
    return headers


def check_status(source, task_id):
    # Perform an actual status check from the ILIAD API or your status checking logic
    try:
        headers = get_api_headers()
        url = f"{settings.ILIAD_URL}/api/v1/sources/{source}/{task_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        status_data = response.json()
        return {
            'status': status_data.get('status', 'UNKNOWN'),
            'message': status_data.get('message', 'Status check completed.'),
            'full_response': status_data
        }
    except requests.RequestException as e:
        return {
            'status': 'ERROR',
            'message': str(e),
            'full_response': {'error': str(e)}
        }


@csrf_exempt
def upload_document(request, source=None):
    if not source:
        return JsonResponse({'status': 'error', 'message': 'Source parameter is required'}, status=400)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # Save the file to the 'previews' folder
        file_path = os.path.join('previews', file.name)
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if not os.path.exists(os.path.dirname(file_full_path)):
            os.makedirs(os.path.dirname(file_full_path))
        path = default_storage.save(file_path, ContentFile(file.read()))

        # Pretend to upload the document to Iliad
        result = upload_document_to_iliad(source, file)

        if result['status'] == 'success' and 'task_id' in result:
            preview_url = os.path.join(settings.MEDIA_URL, file_path)
            response_data = {
                'status': 'success',
                'message': 'Document uploaded successfully.',
                'task_id': result['task_id'],
                'document_id': result.get('document_id'),
                'preview_url': preview_url,
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse(result)

    error_response = {'status': 'error', 'message': 'Invalid request'}
    return JsonResponse(error_response)


@csrf_exempt
def check_upload_status_view(request, source, task_id):
    status_result = check_status(source, task_id)
    return JsonResponse(status_result)


def upload_document_to_iliad(source, file):
    headers = get_api_headers()
    try:
        filename = file.name
        url = f"{settings.ILIAD_URL}/api/v1/sources/{source.lower()}/documents"
        files = {"file": (filename, file, 'application/octet-stream')}

        response = requests.post(url, headers=headers, files=files)

        if response.status_code in [200, 201, 202]:
            response_json = response.json()
            task_id = response_json.get('task_id')
            return {
                "status": "PENDING" if task_id else "COMPLETED",
                "task_id": task_id,
                "preview_url": None,  # This will be constructed separately
                "message": "Upload successful"
            }
        else:
            return {
                "status": "error",
                "message": f"API error: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": str(e)
        }


@csrf_exempt
@api_view(['POST'])
def trigger_auto_upload(request):
    try:
        result = process_documents()
        return Response({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
def get_upload_status(request):
    try:
        records = get_upload_records()
        return Response({
            "status": "success",
            "upload_details": records
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })  # ... (rest of your code remains the same)


def get_api_headers():
    encryption_key = settings.ENCRYPTION_KEY.encode()
    encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
    cipher_suite = Fernet(encryption_key)
    api_key = cipher_suite.decrypt(encrypted_api_key).decode()

    return {
        "x-api-key": api_key,
        "x-user-token": settings.AUTH_TOKEN,
        "Authorization": f"Bearer {settings.AUTH_TOKEN}"
    }


@csrf_exempt
@require_http_methods(["GET"])
def list_documents(request, source):
    try:
        headers = get_api_headers()
        url = f"{settings.ILIAD_URL}/api/v1/sources/{source}/documents"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        documents = response.json()

        # Add created and modified timestamps if they don't exist
        for doc in documents['documents']:
            if 'created_at' not in doc:
                doc['created_at'] = doc.get('timestamp') or None
            if 'modified_at' not in doc:
                doc['modified_at'] = doc.get('timestamp') or None

        return JsonResponse({'documents': documents})
    except requests.RequestException as e:
        logger.error(f"Error fetching documents for source {source}: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch documents'}, status=500)


@csrf_exempt
def list_sources(request):
    logger.info("list_sources view called.")
    if request.method == "GET":
        try:
            # Decrypt the API key
            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)
            # Set up the API request
            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN,
                "Authorization": f"Bearer {settings.AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            url = f"{ILIAD_URL}/api/v1/sources/"
            logger.info(f"Sending request to {url}")
            logger.info(f"Request headers: {headers}")
            # Send the request to the external API
            resp = requests.get(url=url, headers=headers)
            logger.info(f"API response status code: {resp.status_code}")
            logger.info(f"API response body: {resp.text}")
            if resp.status_code == 200:
                external_sources = resp.json()
                logger.info(f"Sources fetched successfully: {external_sources}")
            else:
                logger.error(f"API request failed with status code: {resp.status_code}, Response: {resp.text}")
                return JsonResponse({'error': f"API request failed with status code: {resp.status_code}"},
                                    status=resp.status_code)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
        def serialize_source(source):
            return {
                'name': source.name,
                'visibility': source.visibility,
                'model': source.model or 'N/A',
                'created_at': source.created_at.strftime('%Y-%m-%d %H:%M:%S') if source.created_at else 'N/A',
                'updated_at': source.updated_at.strftime('%Y-%m-%d %H:%M:%S') if source.updated_at else 'N/A',
            }
        def serialize_external_source(source_name, visibility, details=None):
            def format_date(date_str):
                if date_str == 'N/A' or date_str is None:
                    return 'N/A'
                try:
                    formatted_date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    return formatted_date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # In case the date format is not as expected, return it as it is for safety
                    return date_str
            if details is None:
                logger.warning(f"No details available for source: {source_name}")
                return {
                    'name': source_name,
                    'visibility': visibility,
                    'model': 'N/A',
                    'created_at': 'N/A',
                    'updated_at': 'N/A',
                }
            else:
                logger.info(f"Serialized details for source: {source_name} - {details}")
                return {
                    'name': source_name,
                    'visibility': visibility,
                    'model': details.get('embedding_model', 'N/A'),
                    'created_at': format_date(details.get('created', 'N/A')),
                    'updated_at': format_date(details.get('edited', 'N/A')),
                }
        def fetch_external_source_details(source_name):
            source_url = f"{ILIAD_URL}/api/v1/sources/{source_name}"
            logger.info(f"Fetching details for source: {source_url}")
            resp = requests.get(source_url, headers=headers)
            if resp.status_code == 200:
                source_details = resp.json()
                logger.info(f"Details fetched for source: {source_name} - {source_details}")
                return source_details
            else:
                logger.error(f"Failed to fetch details for source: {source_name}, status code: {resp.status_code}")
                return None
        # Fetch sources from the database
        global_sources = Source.objects.filter(visibility='global')
        private_sources = Source.objects.filter(visibility='private')
        global_sources_data = [serialize_source(source) for source in global_sources]
        private_sources_data = [serialize_source(source) for source in private_sources]
        external_global_sources = external_sources.get('global_sources', [])
        external_private_sources = external_sources.get('private_sources', [])
        # Filter external sources to only include those whose names start with "oad"
        external_global_sources = [source for source in external_global_sources if source.startswith("oad")]
        external_private_sources = [source for source in external_private_sources if source.startswith("oad")]
        # Fetch external source details concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            external_global_sources_details = list(executor.map(fetch_external_source_details, external_global_sources))
            external_private_sources_details = list(
                executor.map(fetch_external_source_details, external_private_sources))
        external_global_sources_data = [
            serialize_external_source(source, 'global', details) for source, details in
            zip(external_global_sources, external_global_sources_details)
        ]
        external_private_sources_data = [
            serialize_external_source(source, 'private', details) for source, details in
            zip(external_private_sources, external_private_sources_details)
        ]
        # Combine the external API sources with local database sources
        return JsonResponse({
            'external_sources': {
                'global': external_global_sources_data,
                'private': external_private_sources_data,
            },
            'global_sources': global_sources_data,
            'private_sources': private_sources_data,
        })
    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)







@csrf_exempt
def get_user_token(request):
    logger.info("get_user_token view called.")

    if request.method == 'GET':
        try:
            response_data = {
                'user_token': settings.AUTH_TOKEN,  # Assuming settings.AUTH_TOKEN is the correct token to pass
            }
            logger.info(f"Providing token: {response_data}")
            return JsonResponse(response_data)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def delete_source(request, source):
    logger.info("delete_source view called.")

    if request.method == "DELETE":
        try:
            # Decrypt the API key
            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

            # Set up the API request
            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN,
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            url = f"{ILIAD_URL}/api/v1/sources/{source}"

            logger.info(f"Sending DELETE request to {url}")
            logger.info(f"Request headers: {headers}")

            # Send the request to the external API
            resp = requests.delete(url=url, headers=headers)

            logger.info(f"API response status code: {resp.status_code}")
            logger.info(f"API response body: {resp.text if resp.text else 'No content'}")

            if resp.status_code == 204:
                logger.info(f"Source successfully deleted: {source}")
                return JsonResponse({}, status=204)
            elif resp.status_code == 401:
                logger.error("Unauthorized: Client did not authenticate with x-user-token header.")
                return JsonResponse({'error': 'Unauthorized'}, status=401)
            elif resp.status_code == 403:
                logger.error("Forbidden: The client does not have permission to access the source.")
                return JsonResponse({'error': 'Forbidden'}, status=403)
            elif resp.status_code == 404:
                logger.error("Not Found: Requested source does not exist.")
                return JsonResponse({'error': 'Not Found'}, status=404)
            elif resp.status_code == 422:
                logger.error("Unprocessable Entity: Poorly formatted request.")
                return JsonResponse({'error': 'Unprocessable Entity'}, status=422)
            else:
                logger.error(f"Unexpected status code received: {resp.status_code}")
                return JsonResponse({'error': f"Unexpected status code: {resp.status_code}"}, status=resp.status_code)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)



@csrf_exempt
def chat_with_source(request, source_name):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            filters = data.get('filters', '{}')
            history = data.get('history', [])
            logger.info(f"Received POST data: {data}")

            if not isinstance(filters, str):
                filters = json.dumps(filters)

            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()

            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

            source = source_name
            logger.info(f"Using source: {source}")

            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN,
            }
            if question:
                history.append({"role": "user", "content": question})

            payload = {
                "messages": history,
                "filters": filters,
                "stream": False
            }

            url = f"{ILIAD_URL}/api/v1/sources/{source}/rag"

            logger.info(f"Sending request to {url}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

            resp = requests.post(url=url, headers=headers, json=payload)
            logger.info(f"API response status code: {resp.status_code}")
            logger.info(f"API response body: {resp.text}")

            if resp.status_code == 200:
                response_data = resp.json()
                content = response_data.get('content', 'No content in API response')
                references = response_data.get('references', [])
                logger.info(f"API Response content: {content}")
                logger.info(f"API Response references: {references}")
                response = {'content': content, 'references': references}
            elif resp.status_code == 404:
                logger.info(f"No documents found for the query: {question}")
                response = {'content': "Sorry, no documents were found that match your query.", 'references': []}
            elif resp.status_code == 422:
                logger.error(f"Unprocessable Entity: {resp.text}")
                response = {'content': "The request was poorly formatted and could not be processed.", 'references': []}
            else:
                logger.error(f"API request failed with status code: {resp.status_code}, Response: {resp.text}")
                response = {'content': f"API request failed with status code: {resp.status_code}", 'references': []}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

        return JsonResponse({'question': question, 'response': response, 'history': payload["messages"]})

    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)



@csrf_exempt
@require_http_methods(["DELETE"])
def delete_document(request, source, document_id):
    try:
        # Decrypt the API key
        try:
            encryption_key = settings.ENCRYPTION_KEY.encode()
            encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
            cipher_suite = Fernet(encryption_key)
            api_key = cipher_suite.decrypt(encrypted_api_key).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

        ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
        headers = {
            "x-api-key": api_key,
            "x-user-token": settings.AUTH_TOKEN
        }
        delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{document_id}"

        # Log request details for debugging
        logger.debug(f"DELETE URL: {delete_url}")
        logger.debug(f"Headers: {headers}")

        response = requests.delete(delete_url, headers=headers)

        logger.info(f"Response Status Code: {response.status_code}")

        if response.status_code != 204:
            logger.error(
                f"Failed to delete document:\nResponse Headers: {response.headers}\nResponse Content: {response.text}")

        if response.status_code == 204:
            return JsonResponse({'message': 'Document deleted successfully.'}, status=204)
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    except requests.RequestException as e:
        logger.error(f"Request exception: {e}")
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def api_search(request):
    logger.info("api_search view called.")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get('question')
            mysource = data.get('mysource')
            filters = data.get('filters', {})

            logger.info(f"Received POST data: {data}")

            # Decrypt the API key
            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

            # Determine the source
            if mysource == 'public':
                source = 'oad-public'
            elif mysource == 'internal':
                source = 'oad-internal'
            else:
                logger.error(f"Invalid source provided: {mysource}")
                return JsonResponse({'error': 'Invalid source'}, status=400)

            # Set up the API request
            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN
            }
            payload = {
                "messages": [{"role": "user", "content": question}],
                "filters": json.dumps(filters)
            }

            url = f"{ILIAD_URL}/api/v1/sources/{source}/rag"

            logger.info(f"Sending request to {url}")
            logger.info(f"Request headers: {headers}")
            logger.info(f"Request payload: {payload}")

            # Send the request to the external API
            resp = requests.post(
                url=url,
                headers=headers,
                json=payload
            )

            logger.info(f"API response status code: {resp.status_code}")
            logger.info(f"API response body: {resp.text}")

            if resp.status_code == 200:
                response_data = resp.json()
                content = response_data.get('content', 'No content in API response')
                references = response_data.get('references', [])
                logger.info(f"API Response content: {content}")
                logger.info(f"API Response references: {references}")
                response = {'content': content, 'references': references}
            else:
                logger.error(f"API request failed with status code: {resp.status_code}, Response: {resp.text}")
                return JsonResponse({'error': f"API request failed with status code: {resp.status_code}"}, status=500)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

        return JsonResponse({'question': question, 'response': response})

    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@csrf_exempt
def create_source(request):
    logger.info("create_source view called.")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            source_name = data.get('source')
            description = data.get('description')

            logger.info(f"Received POST data: {data}")

            # Decrypt the API key
            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

            # Set up the API request
            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN,
                "Authorization": f"Bearer {settings.AUTH_TOKEN}",  # Add this line
                "Content-Type": "application/json"
            }
            payload = {
                "source": source_name,
                "description": description,
                "embedding_model": "text-embedding-ada-002"  # default value as per API doc
            }

            url = f"{ILIAD_URL}/api/v1/sources/"

            logger.info(f"Sending request to {url}")
            logger.info(f"Request headers: {headers}")
            logger.info(f"Request payload: {payload}")

            # Send the request to the external API
            resp = requests.post(
                url=url,
                headers=headers,
                json=payload
            )

            logger.info(f"API response status code: {resp.status_code}")
            logger.info(f"API response body: {resp.text}")

            if resp.status_code == 201:
                response_data = resp.json()
                logger.info(f"Source created successfully: {response_data}")
                return JsonResponse(response_data, status=201)
            else:
                logger.error(f"API request failed with status code: {resp.status_code}, Response: {resp.text}")
                return JsonResponse({'error': f"API request failed with status code: {resp.status_code}"},
                                    status=resp.status_code)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    logger.warning("Invalid HTTP method used.")
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)




@csrf_exempt
def sync_source(request, source):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

    try:
        # Decrypt the API key
        try:
            encryption_key = settings.ENCRYPTION_KEY.encode()
            encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
            cipher_suite = Fernet(encryption_key)
            api_key = cipher_suite.decrypt(encrypted_api_key).decode()
            logger.info(f"Successfully synced source: {source}")
            return JsonResponse({'message': f'Successfully synced source: {source}'})
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

        # Set up API request
        ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
        headers = {
            "x-api-key": api_key,
            "x-user-token": settings.AUTH_TOKEN,
            "Authorization": f"Bearer {settings.AUTH_TOKEN}",
            "Content-Type": "application/json"
        }

        # Get existing documents from the source
        existing_docs = get_existing_documents(ILIAD_URL, headers, source)

        # Get local files
        local_files = get_local_files(source)

        # Compare and upload new or updated files
        uploaded_files = []
        for local_file in local_files:
            if should_upload_file(local_file, existing_docs):
                upload_file(ILIAD_URL, headers, source, local_file)
                uploaded_files.append(local_file['name'])

        return JsonResponse({'message': f'Sync completed. Uploaded files: {", ".join(uploaded_files)}'})

    except Exception as e:
        logger.error(f"Error in sync_source: {str(e)}")
        return JsonResponse({'error': 'An error occurred during synchronization'}, status=500)


def search(request):
    return render(request, 'chatbot1/search.html')














def custom_login(request):
    logger.debug("Entering custom_login view")
    try:
        user, created = User.objects.get_or_create(username='saml_user')
        if created:
            logger.debug("Created new user: saml_user")
        else:
            logger.debug("Found existing user: saml_user")

        login(request, user)
        logger.debug("Successfully logged in user: saml_user")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    except Exception as e:
        logger.error(f"Error in custom_login: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def sp_metadata(request):
    logger.debug("Entering sp_metadata view")
    try:
        conf = get_config(config_loader_path=settings.SAML_CONFIG)
        metadata = conf.metadata.to_string()
        logger.debug("Successfully generated SP metadata")
        return HttpResponse(metadata, content_type='text/xml')
    except Exception as e:
        logger.error(f"Error in sp_metadata: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def index(request):
    logger.debug("Entering index view")
    return HttpResponse("Welcome to the SAML2 test")

@login_required
def session_status(request):
    logger.debug("Entering session_status view")
    try:
        if request.user.is_authenticated:
            user_info = {
                'username': request.user.username,
                'email': request.user.email,
                'is_authenticated': True,
            }
            logger.debug(f"Authenticated user info: {user_info}")
            return JsonResponse(user_info)
        else:
            logger.debug("User not authenticated")
            return JsonResponse({'is_authenticated': False}, status=401)
    except Exception as e:
        logger.error(f"Error in session_status: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def custom_logout(request):
    logger.debug("Entering custom_logout view")
    try:
        logout(request)
        logger.debug("Successfully logged out user")
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Logged out successfully!'})
        else:
            return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    except Exception as e:
        logger.error(f"Error in custom_logout: {e}")
        return JsonResponse({'error': str(e)}, status=500)












# views.py

import json
import logging
import os
from .document_uploader import upload_document_to_iliad, check_upload_status as check_status
from django.contrib.auth.decorators import login_required
from .models import UploadRecord
from .auto_uploader import process_documents, start_scheduler, get_source_from_filename
import threading
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests

import concurrent.futures
import datetime
import traceback
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from djangosaml2.views import AssertionConsumerServiceView
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cryptography.fernet import Fernet
from django.views.decorators.http import require_GET, require_http_methods
from saml2.config import SPConfig
from saml2.metadata import create_metadata_string
from .models import Source  # Make sure to import your Source model

logger = logging.getLogger(__name__)

scheduler_thread = None
scheduler_running = False
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"


@csrf_exempt
def auto_upload(request):
    if request.method == 'POST':
        result = process_documents()
        return JsonResponse({
            "status": "success",
            "message": "Auto-upload process completed",
            "processed_files": result['processed_files'],
            "unprocessed_files": result['unprocessed_files']
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def get_upload_status_view(request):
    global scheduler_running
    if request.method == 'GET':
        upload_details = UploadRecord.objects.order_by('-timestamp')[:10].values(
            'file_name', 'source', 'status', 'task_id', 'timestamp'
        )
        return JsonResponse({
            'status': 'success',
            'upload_details': list(upload_details),
            'scheduler_status': 'Running' if scheduler_running else 'Not running'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def start_scheduler_view(request):
    global scheduler_thread, scheduler_running
    if request.method == 'POST':
        if not scheduler_running:
            scheduler_thread = threading.Thread(target=start_scheduler)
            scheduler_thread.start()
            scheduler_running = True
            return JsonResponse({'status': 'success', 'message': 'Scheduler started successfully'})
        else:
            return JsonResponse({'status': 'success', 'message': 'Scheduler is already running'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def upload_document(request, source):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        result = upload_document_to_iliad(source, file)

        print(f"Upload result: {json.dumps(result, indent=2)}")

        if result['status'] == 'success' and 'task_id' in result:
            status_result = check_status(source, result['task_id'])

            response_data = {
                'status': status_result['status'],
                'message': status_result['message'],
                'full_response': status_result['full_response'],
                'task_id': result['task_id']
            }

            print(f"Status check result: {json.dumps(response_data, indent=2)}")

            return JsonResponse(response_data)
        else:
            print(f"Error result: {json.dumps(result, indent=2)}")
            return JsonResponse(result)

    error_response = {'status': 'error', 'message': 'Invalid request'}
    print(f"Invalid request: {json.dumps(error_response, indent=2)}")
    return JsonResponse(error_response)


@csrf_exempt
def check_upload_status(request, source, task_id):
    status_result = check_status(source, task_id)
    return JsonResponse(status_result)


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
def chat_with_source(request, source_name):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            filters = data.get('filters', '{}')
            logger.info(f"Received POST data: {data}")

            if not isinstance(filters, str):
                filters = json.dumps(filters)

            # Decrypt the API key
            try:
                encryption_key = settings.ENCRYPTION_KEY.encode()
                encrypted_api_key = settings.ENCRYPTED_API_KEY.encode()
                cipher_suite = Fernet(encryption_key)
                api_key = cipher_suite.decrypt(encrypted_api_key).decode()

            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return JsonResponse({'error': 'Failed to decrypt API key'}, status=500)

            # Use the source_name directly from the URL parameter
            source = source_name
            logger.info(f"Using source: {source}")

            # Set up the API request
            ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
            headers = {
                "x-api-key": api_key,
                "x-user-token": settings.AUTH_TOKEN
            }
            payload = {
                "messages": [{"role": "user", "content": question}],
                "filters": filters,
                "stream": False
            }

            url = f"{ILIAD_URL}/api/v1/sources/{source}/rag"

            logger.info(f"Sending request to {url}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

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


def list_previews(request):
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    if not os.path.exists(preview_dir):
        return JsonResponse({'previews': []})

    previews = [
        'previews/' + f for f in os.listdir(preview_dir)
        if os.path.isfile(os.path.join(preview_dir, f))
    ]
    return JsonResponse({'previews': previews})


@require_http_methods(["DELETE"])
def delete_document(request, source, document_id):
    try:
        headers = get_api_headers()
        delete_url = f"{ILIAD_URL}/api/v1/sources/{source}/documents/{document_id}"
        response = requests.delete(delete_url, headers=headers)

        if response.status_code == 204:
            return JsonResponse({'message': 'Document deleted successfully.'}, status=204)
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    except requests.RequestException as e:
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


@login_required
@require_http_methods(["GET"])
def current_user(request):
    return JsonResponse({
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
    })


class CustomAssertionConsumerServiceView(AssertionConsumerServiceView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Received SAML response: {request.POST.get('SAMLResponse')}")
        response = super().post(request, *args, **kwargs)
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('http://localhost:3001')  # Redirect to your React frontend URL
        else:
            return HttpResponseRedirect('http://localhost:3001/login-failed')  # Handle failed authentication


def sp_metadata(request):
    conf = SPConfig()
    conf.load(settings.SAML_CONFIG)
    metadata = create_metadata_string(None, conf)
    return HttpResponse(metadata, content_type='text/xml')


def index(request):
    return HttpResponse("Welcome to the SAML2 test")

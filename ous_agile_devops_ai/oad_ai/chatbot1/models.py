# chatbot1/models.py

from django.db import models

class UploadRecord(models.Model):
    file_name = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    preview_url = models.URLField(max_length=1024, null=True, blank=True)  # Add the preview URL field


    def __str__(self):
        return f"{self.file_name} - {self.status}"

class Source(models.Model):
    VISIBILITY_CHOICES = [
        ('global', 'Global'),
        ('private', 'Private'),
    ]

    name = models.CharField(max_length=255, unique=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    model = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.visibility}"
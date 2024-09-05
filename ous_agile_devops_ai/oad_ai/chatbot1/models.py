# chatbot1/models.py

from django.db import models

class UploadRecord(models.Model):
    file_name = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.status}"
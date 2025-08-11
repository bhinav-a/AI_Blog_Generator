from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
import os

class ScrapedData(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    json_file = models.FileField(upload_to='scraped_data/')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('error', 'Error'),
        ('pending', 'Pending')
    ], default='pending')
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.url} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
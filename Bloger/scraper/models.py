from djongo import models  # Change from django.db to djongo
from django.utils import timezone
import json

class ScrapedData(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    
    # Replace FileField with JSONField to store directly in MongoDB
    scraped_content = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('error', 'Error'),
        ('pending', 'Pending')
    ], default='pending')
    error_message = models.TextField(blank=True)
    
    # Add these optional fields for better MongoDB usage
    word_count = models.IntegerField(default=0)
    content_preview = models.TextField(blank=True)  # First 500 chars

    class Meta:
        ordering = ['-created_at']
        db_table = 'scraped_data'  # Collection name in MongoDB

    def __str__(self):
        return f"{self.url} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save_scraped_data(self, data_dict):
        """Save scraped data directly to MongoDB"""
        self.scraped_content = data_dict
        self.title = data_dict.get('title', 'No title')[:200]
        
        # Calculate word count if main_content exists
        main_content = data_dict.get('main_content', '')
        if main_content:
            self.word_count = len(main_content.split())
            self.content_preview = main_content[:500] + ('...' if len(main_content) > 500 else '')
        
        self.status = 'success'
        self.save()
    
    # Compatibility method to support existing code that uses json_file
    @property
    def json_file_content(self):
        """Return the content as if it were read from a file"""
        return json.dumps(self.scraped_content)
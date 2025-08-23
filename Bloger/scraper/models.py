from djongo import models
from django.utils import timezone
import json

class ScrapedData(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    
    # Use TextField instead of JSONField for better compatibility
    scraped_content = models.TextField(default="{}", blank=True)
    
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
    
    @property
    def id_str(self):
        """Return the string representation of the ObjectId"""
        return str(self.pk) if self.pk else None
    
    def get_absolute_url(self):
        from django.urls import reverse
        if self.pk:
            return reverse('scraper:detail', kwargs={'pk': str(self.pk)})
        return '#'  # Fallback URL
    
    def save_scraped_data(self, data_dict):
        """Save scraped data to MongoDB using TextField"""
        self.scraped_content = json.dumps(data_dict)
        self.title = data_dict.get('title', 'No title')[:200]
        
        # Calculate word count if main_content exists
        main_content = data_dict.get('main_content', '')
        if main_content:
            self.word_count = len(main_content.split())
            self.content_preview = main_content[:500] + ('...' if len(main_content) > 500 else '')
        
        self.status = 'success'
        self.save()
    
    def get_scraped_content(self):
        """Get scraped content as dictionary"""
        try:
            return json.loads(self.scraped_content)
        except Exception as e:
            # More detailed error handling
            print(f"Error parsing JSON content: {e}")
            return {}
    
    # Compatibility method to support existing code that uses json_file
    @property
    def json_file_content(self):
        """Return the content as if it were read from a file"""
        return self.scraped_content
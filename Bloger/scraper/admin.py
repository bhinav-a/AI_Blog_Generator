from django.contrib import admin
from .models import ScrapedData

@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ['url', 'title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['url', 'title']
    readonly_fields = ['created_at']
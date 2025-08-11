from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.files.base import ContentFile
from django.urls import reverse
from .models import ScrapedData
from .forms import URLForm
from .utils import WebScraper
import json
import tempfile
import os

def index(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Create a new ScrapedData instance
            scraped_data = ScrapedData.objects.create(
                url=url,
                status='pending'
            )
            
            # Perform scraping
            scraper = WebScraper(url)
            data, error = scraper.scrape()
            
            if error:
                scraped_data.status = 'error'
                scraped_data.error_message = error
                scraped_data.save()
                messages.error(request, f'Error scraping URL: {error}')
            else:
                # Save JSON data to file
                json_content = json.dumps(data, indent=2, ensure_ascii=False)
                filename = f"scraped_{scraped_data.id}_{scraped_data.created_at.strftime('%Y%m%d_%H%M%S')}.json"
                
                scraped_data.json_file.save(
                    filename,
                    ContentFile(json_content.encode('utf-8')),
                    save=False
                )
                scraped_data.title = data.get('title', 'No title')[:200]
                scraped_data.status = 'success'
                scraped_data.save()
                
                messages.success(request, 'Data scraped successfully!')
                return redirect('scraper:detail', pk=scraped_data.pk)
    else:
        form = URLForm()
    
    # Get recent scraping history
    recent_scrapes = ScrapedData.objects.all()[:10]
    
    context = {
        'form': form,
        'recent_scrapes': recent_scrapes
    }
    return render(request, 'scraper/index.html', context)

def detail(request, pk):
    scraped_data = get_object_or_404(ScrapedData, pk=pk)
    
    json_content = None
    if scraped_data.json_file and scraped_data.status == 'success':
        try:
            with scraped_data.json_file.open('r') as f:
                json_content = json.load(f)
        except Exception as e:
            messages.error(request, f'Error reading JSON file: {str(e)}')
    
    context = {
        'scraped_data': scraped_data,
        'json_content': json_content
    }
    return render(request, 'scraper/detail.html', context)

def download_json(request, pk):
    scraped_data = get_object_or_404(ScrapedData, pk=pk)
    
    if not scraped_data.json_file:
        raise Http404("JSON file not found")
    
    try:
        response = HttpResponse(
            scraped_data.json_file.read(),
            content_type='application/json'
        )
        filename = f"scraped_data_{pk}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception:
        raise Http404("Error accessing file")

def api_scrape(request):
    """API endpoint for scraping"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            scraper = WebScraper(url)
            scraped_data, error = scraper.scrape()
            
            if error:
                return JsonResponse({'error': error}, status=400)
            
            return JsonResponse({
                'success': True,
                'data': scraped_data
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
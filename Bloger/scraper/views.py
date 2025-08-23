from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from .models import ScrapedData
from .forms import URLForm
from .utils import WebScraper
import json

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
                # Save data directly to MongoDB
                scraped_data.save_scraped_data(data)
                
                messages.success(request, 'Data scraped successfully!')
                return redirect('scraper:detail', pk=scraped_data.pk)
    else:
        form = URLForm()
    
    # Get recent scraping history and filter out records with None pk
    all_scrapes = ScrapedData.objects.all()[:20]  # Get more than needed
    recent_scrapes = [scrape for scrape in all_scrapes if scrape.pk is not None][:10]
    
    context = {
        'form': form,
        'recent_scrapes': recent_scrapes
    }
    return render(request, 'scraper/index.html', context)

def detail(request, pk):
    scraped_data = get_object_or_404(ScrapedData, pk=pk)
    
    json_content = None
    if scraped_data.status == 'success':
        try:
            # Get content as dictionary
            if hasattr(scraped_data, 'get_scraped_content'):
                json_content = scraped_data.get_scraped_content()
            else:
                # Fallback for direct access (if stored as JSONField)
                json_content = scraped_data.scraped_content
                
                # If it's a string, try to parse it
                if isinstance(json_content, str):
                    json_content = json.loads(json_content)
        except Exception as e:
            messages.error(request, f'Error retrieving data: {str(e)}')
    
    context = {
        'scraped_data': scraped_data,
        'json_content': json_content
    }
    return render(request, 'scraper/detail.html', context)

def download_json(request, pk):
    scraped_data = get_object_or_404(ScrapedData, pk=pk)
    
    if scraped_data.status != 'success':
        raise Http404("JSON data not found")
    
    try:
        # Handle different storage approaches
        content = scraped_data.scraped_content
        
        # If it's already a dict, convert to JSON string
        if isinstance(content, dict):
            json_content = json.dumps(content, indent=2, ensure_ascii=False)
        # If it's a string, use it directly (assuming it's valid JSON)
        elif isinstance(content, str):
            json_content = content
        else:
            # Fallback - try to convert whatever it is to JSON
            json_content = json.dumps(content, indent=2, ensure_ascii=False)
        
        response = HttpResponse(
            json_content,
            content_type='application/json'
        )
        filename = f"scraped_data_{pk}_{scraped_data.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        raise Http404(f"Error accessing data: {str(e)}")

def api_scrape(request):
    """API endpoint for scraping"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # Option: Save to MongoDB here too
            scraped_data = ScrapedData.objects.create(
                url=url,
                status='pending'
            )
            
            scraper = WebScraper(url)
            scraped_content, error = scraper.scrape()
            
            if error:
                scraped_data.status = 'error'
                scraped_data.error_message = error
                scraped_data.save()
                return JsonResponse({'error': error}, status=400)
            
            # Save to MongoDB
            scraped_data.save_scraped_data(scraped_content)
            
            return JsonResponse({
                'success': True,
                'id': str(scraped_data.id),
                'data': scraped_content
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
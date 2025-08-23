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
    if scraped_data.status == 'success':
        try:
            # Get JSON directly from MongoDB
            json_content = scraped_data.scraped_content
        except Exception as e:
            messages.error(request, f'Error retrieving data: {str(e)}')
    
    context = {
        'scraped_data': scraped_data,
        'json_content': json_content
    }
    return render(request, 'scraper/detail.html', context)

def download_json(request, pk):
    scraped_data = get_object_or_404(ScrapedData, pk=pk)
    
    if scraped_data.status != 'success' or not scraped_data.scraped_content:
        raise Http404("JSON data not found")
    
    try:
        # Generate JSON content from MongoDB data
        json_content = json.dumps(
            scraped_data.scraped_content, 
            indent=2, 
            ensure_ascii=False
        )
        
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
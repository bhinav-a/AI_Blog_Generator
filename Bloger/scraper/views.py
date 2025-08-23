from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
# Import direct MongoDB client instead of Django model
from .mongodb_client import MongoDBClient
from .forms import URLForm
from .utils import WebScraper
import json

# Initialize MongoDB client
mongo_client = MongoDBClient()

def index(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Perform scraping
            scraper = WebScraper(url)
            data, error = scraper.scrape()
            
            if error:
                # Save error to MongoDB
                document_id = mongo_client.save_scraped_data(
                    url=url,
                    data_dict={},
                    status='error',
                    error_message=error
                )
                messages.error(request, f'Error scraping URL: {error}')
            else:
                # Save data to MongoDB
                document_id = mongo_client.save_scraped_data(
                    url=url,
                    data_dict=data,
                    status='success'
                )
                
                messages.success(request, 'Data scraped successfully!')
                return redirect('scraper:detail', pk=document_id)
    else:
        form = URLForm()
    
    # Get recent scraping history
    recent_scrapes = mongo_client.get_recent_scrapes(10)
    
    for scrape in recent_scrapes:
        print(f"Scrape ID: '{scrape.get('id', 'MISSING')}', Type: {type(scrape.get('id', ''))}")
    
    context = {
        'form': form,
        'recent_scrapes': recent_scrapes
    }
    return render(request, 'scraper/index.html', context)

def detail(request, pk):
    document = mongo_client.get_scraped_data(pk)
    
    if not document:
        raise Http404("Scraped data not found")
    
    context = {
        'scraped_data': document,
        'json_content': document.get('json_content', {})
    }
    return render(request, 'scraper/detail.html', context)

def download_json(request, pk):
    document = mongo_client.get_scraped_data(pk)
    
    if not document or document.get('status') != 'success':
        raise Http404("JSON data not found")
    
    try:
        # Get JSON content
        if 'json_content' in document:
            json_content = json.dumps(document['json_content'], indent=2, ensure_ascii=False)
        else:
            json_content = document.get('scraped_content', '{}')
        
        response = HttpResponse(
            json_content,
            content_type='application/json'
        )
        filename = f"scraped_data_{pk}.json"
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
            
            # Perform scraping
            scraper = WebScraper(url)
            scraped_content, error = scraper.scrape()
            
            if error:
                return JsonResponse({'error': error}, status=400)
            
            # Save to MongoDB
            document_id = mongo_client.save_scraped_data(
                url=url,
                data_dict=scraped_content,
                status='success'
            )
            
            return JsonResponse({
                'success': True,
                'id': document_id,
                'data': scraped_content
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
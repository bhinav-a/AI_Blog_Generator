from django.core.management.base import BaseCommand
from scraper.models import ScrapedData
from scraper.utils import WebScraper
from django.core.files.base import ContentFile
import json

class Command(BaseCommand):
    help = 'Scrape a URL from command line'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL to scrape')

    def handle(self, *args, **options):
        url = options['url']
        
        self.stdout.write(f'Scraping: {url}')
        
        scraper = WebScraper(url)
        data, error = scraper.scrape()
        
        if error:
            self.stdout.write(
                self.style.ERROR(f'Error: {error}')
            )
            return
        
        # Save to database
        scraped_data = ScrapedData.objects.create(
            url=url,
            title=data.get('title', 'No title')[:200],
            status='success'
        )
        
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        filename = f"scraped_{scraped_data.id}_{scraped_data.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        
        scraped_data.json_file.save(
            filename,
            ContentFile(json_content.encode('utf-8'))
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully scraped and saved data for {url}')
        )
        self.stdout.write(f'Data ID: {scraped_data.id}')
# 🕷️ Django Web Scraper

A clean and focused Django web application that extracts meaningful content from web pages, filtering out navigation clutter, ads, and irrelevant elements. Perfect for scraping educational content, articles, and tutorials.

## 🌟 Features

- **Clean Content Extraction**: Focuses only on main content and meaningful paragraphs
- **Smart Filtering**: Automatically removes navigation, ads, headers, and footers
- **Web Interface**: User-friendly Bootstrap-based UI for easy URL submission
- **JSON Storage**: Saves scraped data as downloadable JSON files
- **Database Tracking**: Maintains history of all scraping operations
- **Error Handling**: Robust error management and status tracking
- **Admin Interface**: Django admin panel for managing scraped data
- **REST API**: Programmatic access via API endpoints
- **CLI Support**: Command-line scraping capability
- **GeeksforGeeks Optimized**: Specially optimized for educational content sites

## 🎯 What Gets Scraped

The scraper extracts only the essential content:

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "main_content": "Complete article text without clutter...",
  "paragraphs": [
    "First meaningful paragraph with substantial content...",
    "Second paragraph with actual article content..."
  ],
  "headings": {
    "h1": ["Main Title"],
    "h2": ["Section Headers"],
    "h3": ["Subsection Headers"]
  },
  "word_count": 1247,
  "scraped_at": "2025-08-11 14:30:22"
}
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/django-web-scraper.git
   cd django-web-scraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create media directory**
   ```bash
   mkdir -p media/scraped_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Web Interface: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/

## 📖 Usage

### Web Interface

1. Navigate to http://localhost:8000/
2. Enter the URL you want to scrape
3. Click "Scrape Data"
4. View the extracted content
5. Download the JSON file if needed

### API Usage

**Scrape a URL:**
```bash
curl -X POST http://localhost:8000/api/scrape/ \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.geeksforgeeks.org/python-tutorial/"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://www.geeksforgeeks.org/python-tutorial/",
    "title": "Python Tutorial - GeeksforGeeks",
    "main_content": "Python is a high-level programming language...",
    "paragraphs": ["First paragraph...", "Second paragraph..."],
    "headings": {"h1": ["Python Tutorial"], "h2": ["Introduction", "Features"]},
    "word_count": 1542,
    "scraped_at": "2025-08-11 14:30:22"
  }
}
```

### Command Line Interface

```bash
# Scrape a single URL
python manage.py scrape_url https://www.geeksforgeeks.org/python-tutorial/

# The scraped data will be saved to the database and media folder
```

## 🎨 Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Scraped Data View
![Data View](screenshots/data-view.png)

### Admin Panel
![Admin Panel](screenshots/admin-panel.png)

## 🛠️ Technical Details

### Tech Stack

- **Backend**: Django 4.2.7
- **Web Scraping**: BeautifulSoup4, Requests
- **Frontend**: Bootstrap 5, HTML5
- **Database**: SQLite (development), PostgreSQL (production ready)
- **File Storage**: Local filesystem (Django FileField)

### Project Structure

```
django-web-scraper/
├── manage.py
├── requirements.txt
├── README.md
├── web_scraper_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scraper/
│   ├── models.py          # Database models
│   ├── views.py           # Web views and API
│   ├── forms.py           # Django forms
│   ├── utils.py           # Scraping logic
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   ├── templates/         # HTML templates
│   └── management/        # CLI commands
└── media/                 # Scraped JSON files
```

### Key Components

- **WebScraper Class**: Core scraping logic with smart content extraction
- **ScrapedData Model**: Database model for tracking scrape operations
- **Clean Content Extraction**: Filters out navigation, ads, and clutter
- **Error Handling**: Comprehensive error management and logging

## 🎯 Optimized For

- **Educational Sites**: GeeksforGeeks, tutorials, documentation
- **News Articles**: Blog posts, news sites, medium articles
- **Technical Content**: Programming tutorials, how-to guides
- **Clean Content**: Any site with structured article content

## ⚙️ Configuration

### Settings

Key configuration options in `settings.py`:

```python
# Media files for JSON storage
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add scraper to installed apps
INSTALLED_APPS = [
    # ... other apps
    'scraper',
]
```

### Custom Scraping Rules

Modify `utils.py` to customize:
- Content selectors
- Filtering rules
- Output format
- Site-specific optimizations

## 🔧 Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 guidelines. Format code with:

```bash
pip install black
black .
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| GET | `/detail/<id>/` | View scraped data details |
| GET | `/download/<id>/` | Download JSON file |
| POST | `/api/scrape/` | API endpoint for scraping |
| GET | `/admin/` | Django admin interface |

## 🚨 Important Notes

### Legal and Ethical Usage

- **Respect robots.txt**: Always check website's robots.txt file
- **Rate Limiting**: Don't overwhelm servers with too many requests
- **Terms of Service**: Comply with website terms of service
- **Personal Use**: Keep scraping for educational/personal purposes
- **Data Privacy**: Don't scrape personal or sensitive information

### Best Practices

- Use reasonable delays between requests
- Respect website rate limits
- Cache results to avoid repeated scraping
- Handle errors gracefully
- Monitor your scraping activity

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'bs4'`
```bash
pip install beautifulsoup4
```

**Issue**: `CSRF verification failed`
- Ensure CSRF token is included in forms
- Check Django settings configuration

**Issue**: `Permission denied` for media files
```bash
# On Unix/Linux
chmod 755 media/
chmod 755 media/scraped_data/
```

**Issue**: Scraping returns empty content
- Check if the site uses JavaScript for content loading
- Verify the site doesn't block requests from your IP
- Check if the site structure has changed

## 📊 Performance

- **Average scraping time**: 2-5 seconds per page
- **Supported file size**: Up to 50MB JSON files
- **Concurrent requests**: Configurable (default: 1)
- **Memory usage**: ~50MB per scraping operation

## 🔮 Future Enhancements

- [ ] JavaScript rendering support (Selenium integration)
- [ ] Bulk URL processing
- [ ] Scheduled scraping jobs
- [ ] Export to multiple formats (CSV, XML, PDF)
- [ ] Advanced filtering rules
- [ ] Proxy support
- [ ] Docker containerization
- [ ] Cloud storage integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

If you find this project helpful, please give it a ⭐ on GitHub!

For support or questions:
- Create an [Issue](https://github.com/yourusername/django-web-scraper/issues)
- Email: your.email@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 📈 Changelog

### v1.0.0 (2025-08-11)
- Initial release
- Clean content extraction
- Web interface and API
- Django admin integration
- CLI support
- GeeksforGeeks optimization

---

**Built with ❤️ using Django and BeautifulSoup**

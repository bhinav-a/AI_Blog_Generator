from pymongo import MongoClient
import os
from bson import ObjectId
from datetime import datetime
import json

class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/ai_blog_db')
            cls._instance.client = MongoClient(mongodb_uri)
            db_name = os.environ.get('MONGODB_NAME', 'ai_blog_db')
            cls._instance.db = cls._instance.client[db_name]
            cls._instance.collection = cls._instance.db['scraped_data']
        return cls._instance
    
    def save_scraped_data(self, url, data_dict, status='success', error_message=''):
        """Save scraped data directly to MongoDB"""
        document = {
            'url': url,
            'title': data_dict.get('title', 'No title')[:200] if data_dict else '',
            'scraped_content': json.dumps(data_dict) if data_dict else '{}',
            'status': status,
            'error_message': error_message,
            'created_at': datetime.now(),
            'word_count': len(data_dict.get('main_content', '').split()) if data_dict and 'main_content' in data_dict else 0,
            'content_preview': data_dict.get('main_content', '')[:500] + '...' if data_dict and 'main_content' in data_dict and len(data_dict.get('main_content', '')) > 500 else data_dict.get('main_content', '')[:500] if data_dict else ''
        }
        
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def get_scraped_data(self, id_str):
        """Get a single document by ID"""
        try:
            object_id = ObjectId(id_str)
            document = self.collection.find_one({'_id': object_id})
            if document:
                # Convert ObjectId to string for the template
                document['id'] = str(document['_id'])
                # Parse JSON content if needed
                if isinstance(document.get('scraped_content'), str):
                    try:
                        document['json_content'] = json.loads(document['scraped_content'])
                    except:
                        document['json_content'] = {}
            return document
        except:
            return None
    
    def get_recent_scrapes(self, limit=10):
        """Get recent scraping history"""
        documents = list(self.collection.find().sort('created_at', -1).limit(limit))
        for doc in documents:
            # Convert ObjectId to string for the template
            doc['id'] = str(doc['_id'])
        return documents
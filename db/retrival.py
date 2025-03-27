import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import traceback
import hashlib

from flask import jsonify

# Load environment variables
load_dotenv()
ELASTIC_USERNAME = os.environ.get("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
es = Elasticsearch(
        "http://127.0.0.1:9200",  # Use HTTPS if your Elasticsearch is configured with TLS/SSL
        verify_certs=False,  # Disable cert verification for local/dev use (not recommended for production)
        basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)  # Use credentials from .env
    )
INDEX_NAME = "breaknews"
def generate_id(news_item):
    """
    Generate a unique ID for each news item based on its URL or content.
    If the URL is not available, use a hash of the title and content.
    """
    if news_item.get("url"):
        # Use the URL to generate a unique hash
        return hashlib.sha256(news_item["url"].encode("utf-8")).hexdigest()
    else:
        # Fallback: Use the title and content
        unique_string = news_item["title"] + news_item["content"]
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

def save_in_es(news_data):
    for news_item in news_data:
        try:
            # Generate a unique ID for the document
            doc_id = generate_id(news_item)

            # Use the `doc_id` when indexing the document
            response = es.index(index=INDEX_NAME, id=doc_id, document=news_item)
            
            # Check the response status
            if response["result"] == "created":
                print(f"Indexed new document with ID: {response['_id']}")
            elif response["result"] == "updated":
                print(f"Updated existing document with ID: {response['_id']}")
        except Exception as e:
            print(f"Error indexing document: {e}")
from flask import jsonify

def get_breaking_news():
    # Elasticsearch query
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "bool": {
                        "should": [
                    # Boost articles with 'breaking' in the title
                    {"match": {"title": {"query": "breaking", "boost": 2.0}}},  
                    
                    # Boost articles with 'featured' in tags
                    {"match": {"tags": {"query": "featured", "boost": 1.5}}},  
                    
                    # Boost articles with 'urgent' in description
                    {"match": {"description": {"query": "urgent", "boost": 2.0}}},  
                    
                    # Boost articles with 'politics' in the title
                    {"match": {"title": {"query": "politics", "boost": 1.8}}},  
                    
                    # Boost articles with 'environment' in description
                    {"match": {"description": {"query": "environment", "boost": 1.8}}},  
                    
                    # Boost articles with 'politics' in tags
                    {"match": {"tags": {"query": "politics", "boost": 1.8}}},  
                    
                    # Boost articles with 'environment' in tags
                    {"match": {"tags": {"query": "environment", "boost": 1.8}}}  
                ],
                    "filter": [
                        {"range": {"publishedAt": {"gte": "now-1d/d"}}}
                    ]
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},  # Sort by relevance score
                {"publishedAt": {"order": "desc"}}  # Sort by publication date if scores are equal
            ]
        }
    )

    # Process results and add serial numbers
    results_with_serial = []
    for idx, hit in enumerate(response["hits"]["hits"], start=1):  # Start serial number from 1
        news_item = hit["_source"]
        news_item["serial_number"] = idx  # Add the serial number to the news item
        results_with_serial.append(news_item)

    # Return results as JSON
    return jsonify(results_with_serial)

def del_old_news():
    # Delete documents older than 7 days
    try:
        response = es.delete_by_query(
            index=INDEX_NAME,
            body={
                "query": {
                    "range": {
                        "publishedAt": {
                            "lt": "now-7d/d"  # News older than 7 days
                        }
                    }
                }
            }
        )
        print(f"Deleted {response['deleted']} old documents.")
    except Exception as e:
        print(f"Error deleting old news: {str(e)}")

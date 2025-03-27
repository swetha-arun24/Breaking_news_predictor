import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import traceback

from flask import jsonify

# Load environment variables
load_dotenv()
ELASTIC_USERNAME = os.environ.get("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")

# Confirm operation
consent = input("This will overwrite existing tables. Continue? [y/n]: ")
if consent.lower() != "y":
    raise InterruptedError("Operation cancelled!")


try:
    # Elasticsearch connection setup
    es = Elasticsearch(
        "http://127.0.0.1:9200",  # Use HTTPS if your Elasticsearch is configured with TLS/SSL
        verify_certs=False,  # Disable cert verification for local/dev use (not recommended for production)
        basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)  # Use credentials from .env
    )

    # Define the index name and mapping
    INDEX_NAME = "breaknews"
    mapping = {
    "properties": {
        "publishedAt": {"type": "date"},
        "author": {"type": "text"},
        "urlToImage": {"type": "keyword"},
        "description": {
            "type": "text"  # Removed boost here
        },
        "source": {
            "properties": {
                "name": {"type": "text"},
                "id": {"type": "text"}
            }
        },
        "title": {
            "type": "text",
            "analyzer": "standard"  # Standard analyzer for better text analysis
        },
        "content": {"type": "text"},
        "url": {"type": "keyword"}
    }
}

    # Check if the index exists
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists!")
    else:
        # Create the index
        es.indices.create(index=INDEX_NAME, body={"mappings": mapping})
        print(f"Successfully created index: {INDEX_NAME}")

    # Print all indices (for verification)
    indices = es.cat.indices(format="json")  # Use format="json" for structured output
    print("Existing indices:")
    for idx in indices:
        print(f"Index: {idx['index']}, Docs Count: {idx['docs.count']}, Size: {idx['store.size']}")

except Exception as e:
    print("Could not create index.")
    print("Error: ", str(e))
    print("Traceback:")
    traceback.print_exc()
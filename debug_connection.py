from notion_client import Client
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize client with debug logging
notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.DEBUG)

# Print environment variables (masked for security)
token = os.getenv('NOTION_TOKEN')
db_id = os.getenv('NOTION_DATABASE_ID')
print(f"Token (first 4 chars): {token[:4]}...")
print(f"Database ID: {db_id}")

# Test the connection
try:
    # Try to list users
    users = notion.users.list()
    print("\n✅ Connection successful!")
    print(f"Found {len(users['results'])} users")
    
    # Try to access the database
    db = notion.databases.retrieve(database_id=db_id)
    print("✅ Database access successful!")
    print(f"Database title: {db['title'][0]['plain_text']}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}") 
from notion_client import Client
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))
database_id = os.getenv('NOTION_DATABASE_ID')  # Get from environment instead of hardcoding

try:
    # Test database access
    db = notion.databases.retrieve(database_id=database_id)
    print("\n✅ Database access verified!")
    print(f"Database title: {db['title'][0]['plain_text'] if db['title'] else 'Untitled'}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Go to your database in Notion")
    print("2. Click '...' → 'Add connections' → Select 'Job Applications Tracker'")
    print("3. Wait a few seconds")
    print("4. Run this script again") 
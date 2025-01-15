from notion_client import Client
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))

try:
    # 1. First verify the integration
    me = notion.users.me()
    print(f"\n✅ Integration verified as: {me.get('name')}")
    
    # 2. List all accessible databases
    print("\nSearching for all accessible databases...")
    response = notion.search(
        **{
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
    )
    
    if response['results']:
        print("\nAccessible databases:")
        for db in response['results']:
            title = db['title'][0]['plain_text'] if db['title'] else 'Untitled'
            print(f"\nDatabase: {title}")
            print(f"ID: {db['id']}")
            print(f"URL: {db.get('url', 'No URL available')}")
            print("---")
            
        print("\n📋 Next steps:")
        print("1. Copy the correct database ID from above")
        print("2. Update your .env file with:")
        print("NOTION_DATABASE_ID=your_database_id_here")
    else:
        print("\n❌ No databases found")
        print("\n🔧 To fix this:")
        print("1. Go to your database in Notion")
        print("2. Click '...' in the top right")
        print("3. Click 'Add connections'")
        print("4. Select 'Job Applications Tracker'")
        print("5. Wait a few seconds and run this script again")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
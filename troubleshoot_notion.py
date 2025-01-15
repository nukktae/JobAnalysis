from notion_client import Client
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

def verify_integration():
    notion = Client(auth=os.getenv('NOTION_TOKEN'))
    token = os.getenv('NOTION_TOKEN')
    db_id = os.getenv('NOTION_DATABASE_ID')
    
    print("\n🔍 Starting Notion Integration Verification...")
    print(f"Database ID being used: {db_id}")
    print(f"Token prefix: {token[:4]}...")
    
    try:
        # 1. Verify bot access
        me = notion.users.me()
        print(f"\n✅ Bot verified as: {me.get('name')}")
        
        # 2. List accessible databases
        print("\nSearching for accessible databases...")
        response = notion.search(filter={"property": "object", "value": "database"})
        
        if not response['results']:
            print("\n❌ No databases found!")
            print("\n👉 To fix this:")
            print("1. Go to your Notion database")
            print("2. Click 'Share' in the top right")
            print("3. Click 'Add connections'")
            print("4. Find and select your integration")
            print("5. Run this script again")
            return False
        
        print("\nAccessible databases:")
        found_target = False
        for db in response['results']:
            title = db['title'][0]['plain_text'] if db['title'] else 'Untitled'
            current_id = db['id']
            print(f"\n- {title} ({current_id})")
            if current_id == db_id:
                found_target = True
                print("  ✅ This is your target database!")
        
        if not found_target:
            print(f"\n❌ Target database {db_id} not found in accessible databases!")
            return False
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_integration():
        print("\n✅ All checks passed! Your integration is properly configured.")
    else:
        print("\n❌ Some checks failed. Please follow the instructions above to fix the issues.") 
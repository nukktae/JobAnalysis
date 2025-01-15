from notion_client import Client
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))

# Database schema based on job_tracker.py properties
database_properties = {
    "Title": {"title": {}},
    "Company": {"rich_text": {}},
    "Location": {"multi_select": {}},
    "Work Mode": {
        "select": {
            "options": [
                {"name": "Remote", "color": "green"},
                {"name": "Hybrid", "color": "yellow"},
                {"name": "On-site", "color": "red"},
                {"name": "Not Specified", "color": "gray"}
            ]
        }
    },
    "Timeline": {"rich_text": {}},
    "Required Education": {"rich_text": {}},
    "Required Experience": {"rich_text": {}},
    "Key Skills": {"multi_select": {}},
    "Salary Range": {"rich_text": {}},
    "Visa Sponsorship": {"rich_text": {}},
    "Status": {
        "select": {
            "options": [
                {"name": "Not Applied", "color": "gray"},
                {"name": "Applied", "color": "yellow"},
                {"name": "Interview", "color": "blue"},
                {"name": "Offer", "color": "green"},
                {"name": "Rejected", "color": "red"}
            ]
        }
    },
    "Priority": {
        "select": {
            "options": [
                {"name": "High", "color": "red"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "blue"}
            ]
        }
    },
    "Application Link": {"url": {}},
    "Notes": {"rich_text": {}},
    "Next Steps": {
        "select": {
            "options": [
                {"name": "Prepare Resume", "color": "blue"},
                {"name": "Take Home Test", "color": "yellow"},
                {"name": "Technical Interview", "color": "orange"},
                {"name": "HR Interview", "color": "green"},
                {"name": "Follow Up", "color": "purple"},
                {"name": "None", "color": "gray"}
            ]
        }
    },
    "Company Size": {
        "select": {
            "options": [
                {"name": "Startup (<50)", "color": "blue"},
                {"name": "Small (50-200)", "color": "green"},
                {"name": "Medium (201-1000)", "color": "yellow"},
                {"name": "Large (1000+)", "color": "red"}
            ]
        }
    },
    "Industry": {"multi_select": {}},
    "Benefits": {"multi_select": {}},
    "Application Date": {"date": {}}
}

try:
    print("\nCreating new database...")
    response = notion.databases.create(
        parent={"type": "page_id", "page_id": os.getenv('NOTION_PAGE_ID')},
        title=[{"type": "text", "text": {"content": "Job Applications"}}],
        properties=database_properties,
        is_inline=False
    )
    
    print("\n✅ Database created successfully!")
    print(f"Database ID: {response['id']}")
    print("\n📋 Next steps:")
    print("1. Add this ID to your .env file:")
    print(f"NOTION_DATABASE_ID={response['id']}")
    print("2. Go to the database in Notion")
    print("3. Click '...' → 'Add connections' → Select 'Job Applications Tracker'")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTo fix this:")
    print("1. Create a new page in Notion")
    print("2. Copy the page ID from the URL (after notion.so/)")
    print("3. Add it to your .env file as NOTION_PAGE_ID")
    print("4. Run this script again") 
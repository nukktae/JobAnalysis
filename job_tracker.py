from notion_client import Client
import json
from typing import Dict, Any
import sys
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

class NotionJobTracker:
    def __init__(self):
        self.notion = Client(auth=os.getenv('NOTION_TOKEN'))
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        print(f"Using database ID: {self.database_id}")

    def add_job(self, job_data: Dict[str, Any]):
        # Ensure locations is a non-empty list
        if not job_data.get("locations"):
            job_data["locations"] = ["Not Specified"]
        
        # Process locations to remove commas
        processed_locations = []
        for location in job_data["locations"]:
            if location:  # Only process non-empty locations
                processed_location = location.replace(",", " -")
                processed_locations.append(processed_location)
        
        if not processed_locations:
            processed_locations = ["Not Specified"]

        # Handle date fields
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_properties = {
            "Application Date": {"date": {"start": current_date}}
        }

        # Clean up any fields that might contain commas for select options
        def clean_select_value(value):
            if isinstance(value, str):
                return value.replace(",", " -")
            return value

        properties = {
            "Title": {"title": [{"text": {"content": job_data["job_title"]}}]},
            "Company": {"rich_text": [{"text": {"content": job_data["company_name"]}}]},
            "Location": {"multi_select": [{"name": loc} for loc in processed_locations]},
            "Work Mode": {"select": {"name": clean_select_value(job_data.get("work_mode", "Not Specified"))}},
            "Timeline": {"rich_text": [{"text": {"content": job_data.get("timeline", "Not Specified")}}]},
            "Required Education": {"rich_text": [{"text": {"content": job_data.get("required_education", "Not Specified")}}]},
            "Required Experience": {"rich_text": [{"text": {"content": job_data.get("required_experience", "Not Specified")}}]},
            "Key Skills": {"multi_select": [{"name": clean_select_value(skill)} for skill in job_data.get("key_skills", [])]},
            "Salary Range": {"rich_text": [{"text": {"content": job_data.get("salary_range", "Not Specified")}}]},
            "Visa Sponsorship": {"rich_text": [{"text": {"content": job_data.get("visa_sponsorship", "Not Specified")}}]},
            "Status": {"select": {"name": "Not Applied"}},
            "Application Link": {"url": job_data.get("application_link")},
            "Notes": {"rich_text": [{"text": {"content": job_data.get("notes", "")}}]},
            "Next Steps": {"select": {"name": clean_select_value(job_data.get("next_steps", "Prepare Resume"))}},
            "Company Size": {"select": {"name": clean_select_value(job_data.get("company_size", "Not Specified"))}},
            "Priority": {"select": {"name": clean_select_value(job_data.get("priority", "Medium"))}},
            "Industry": {"multi_select": [{"name": clean_select_value(ind)} for ind in job_data.get("industry", [])]},
            "Benefits": {"multi_select": [{"name": clean_select_value(benefit)} for benefit in job_data.get("benefits", [])]}
        }

        # Add date properties
        properties.update(date_properties)

        try:
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            print("✅ Successfully added job to Notion!")
            return response
        except Exception as e:
            print(f"❌ Error adding job to Notion: {str(e)}")
            raise e

def main():
    tracker = NotionJobTracker()

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            job_data = json.load(f)
            tracker.add_job(job_data)
    else:
        print("Please provide a JSON file path as an argument")

if __name__ == "__main__":
    main()
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from job_tracker import NotionJobTracker
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright
import re
from job_sites import JobSiteExtractor
from functools import lru_cache
from parse_job_posting import parse_job_posting

app = Flask(__name__, static_url_path='/static', static_folder='static')
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def clean_job_data(job_data: dict) -> dict:
    # Extract nested data
    if "basic_information" in job_data:
        basic = job_data["basic_information"]
        additional = job_data.get("additional_details", {})
        defaults = job_data.get("default_fields", {})
        
        # Combine all data into one flat dictionary
        job_data = {
            # Basic information
            "job_title": basic.get("job_title"),
            "company_name": basic.get("company_name"),
            "locations": basic.get("locations", []),
            "work_mode": basic.get("work_mode", "Not Specified"),
            "timeline": basic.get("timeline", "Not Specified"),
            "required_education": basic.get("required_education", "Not Specified"),
            "required_experience": basic.get("required_experience", "Not Specified"),
            "key_skills": basic.get("key_skills", []),
            "salary_range": basic.get("salary_range", "Not Specified"),
            "visa_sponsorship": basic.get("visa_sponsorship", "Not Specified"),
            
            # Additional details
            "application_link": additional.get("application_link", "Not Specified"),
            "company_size": additional.get("company_size", "Not Specified"),
            "industry": additional.get("industry", []),
            "benefits": additional.get("benefits", []),
            "notes": additional.get("notes", ""),
            
            # Default fields
            "priority": defaults.get("priority", "Medium"),
            "next_steps": defaults.get("next_steps", "Prepare Resume"),
            "application_date": None
        }
    
    # Process text fields that might be lists
    text_fields = [
        "job_title", "company_name", "job_id", "work_mode", "timeline",
        "required_education", "required_experience", "salary_range", 
        "visa_sponsorship", "application_link", "notes", "contact_person"
    ]
    
    for field in text_fields:
        if isinstance(job_data.get(field), list):
            job_data[field] = ". ".join(job_data[field])
    
    # Ensure list fields are lists
    list_fields = ["locations", "key_skills", "benefits", "industry"]
    for field in list_fields:
        if isinstance(job_data.get(field), str):
            job_data[field] = [item.strip() for item in job_data[field].split(",")]
    
    # Ensure date fields are either valid ISO dates or null
    date_fields = ["application_deadline", "application_date", "last_contact"]
    for field in date_fields:
        if job_data.get(field) in ["Not Specified", "", "null", None]:
            job_data[field] = None
    
    # Truncate company size if too long
    if len(job_data.get('company_size', '')) > 100:
        job_data['company_size'] = job_data['company_size'][:97] + '...'
    
    # Ensure company size is one of the valid options
    valid_company_sizes = ["Startup (<50)", "Small (50-200)", "Medium (201-1000)", "Large (1000+)", "Not Specified"]
    if job_data.get('company_size') not in valid_company_sizes:
        job_data['company_size'] = "Not Specified"
    
    return job_data

def extract_from_linkedin(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # Wait for job content to load
        page.wait_for_selector('div.job-view-layout')
        html_content = page.content()
        browser.close()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    job_description = soup.find('div', {'class': 'description__text'})
    return job_description.get_text() if job_description else None

def extract_from_indeed(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_description = soup.find('div', {'id': 'jobDescriptionText'})
    return job_description.get_text() if job_description else None

@lru_cache(maxsize=100)
def cached_extract_from_url(url):
    extractor = JobSiteExtractor()
    try:
        if not url or 'javascript:' in url:
            raise Exception("Invalid URL provided")
            
        # Extract based on domain
        if 'brassring.com' in url:
            job_text = extractor.extract_brassring(url)
        elif 'linkedin.com' in url:
            return jsonify({
                "success": False,
                "error": "LinkedIn jobs require authentication. Please follow these steps instead:\n\n1. Open the job posting in your browser\n2. Click 'Show more' to expand the full description\n3. Copy the entire job posting\n4. Paste it in the text box below"
            }), 400
        elif 'indeed.com' in url:
            job_text = extractor.extract_indeed(url)
        elif 'workdayjobs.com' in url or 'myworkdayjobs.com' in url:
            job_text = extractor.extract_workday(url)
        elif 'greenhouse.io' in url:
            job_text = extractor.extract_greenhouse(url)
        elif 'ttcportals.com' in url:
            job_text = extractor.extract_with_playwright(url)
        elif 'submit4jobs.com' in url:
            raise Exception("This job board requires direct access. Please copy and paste the job description.")
        else:
            job_text = extractor.extract_generic(url)
            
        if not job_text or job_text.strip() == "":
            raise Exception(f"Failed to extract job description from {url.split('/')[2]}")
            
        return job_text
        
    except Exception as e:
        print(f"URL extraction error: {str(e)}")
        raise Exception(f"Failed to extract job description: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        job_url = request.form.get('job_url')
        job_text = request.form.get('job_text')

        if job_url and not job_text:
            try:
                job_text = cached_extract_from_url(job_url)
                if not job_text:
                    return jsonify({
                        "success": False,
                        "error": "Could not extract job description. Please copy and paste the job posting text directly."
                    }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 400

        # Parse the job text using OpenAI
        job_data = parse_job_posting(job_text)
        
        if not job_data:
            return jsonify({
                "success": False,
                "error": "Failed to parse job posting. Please try again."
            }), 400

        # Format salary range if it's an object
        if isinstance(job_data.get("salary_range"), dict):
            salary_parts = []
            for category, amount in job_data["salary_range"].items():
                category = category.replace("_", " ").title()
                salary_parts.append(f"{category}: {amount}")
            job_data["salary_range"] = " | ".join(salary_parts)

        # Add the original URL as the application link
        if job_url:
            job_data["application_link"] = job_url

        # Add the job to Notion
        tracker = NotionJobTracker()
        try:
            tracker.add_job(job_data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to add job to Notion: {str(e)}"
            }), 400

        return jsonify({
            "success": True,
            "data": job_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 
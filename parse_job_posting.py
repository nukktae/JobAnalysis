from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def clean_job_data(job_data: dict) -> dict:
    # Set default values for required fields
    defaults = {
        "job_title": "Not Specified",
        "company_name": "Not Specified",
        "locations": [],
        "work_mode": "Not Specified",
        "timeline": "Not Specified",
        "required_education": "Not Specified",
        "required_experience": "Not Specified",
        "salary_range": "Not Specified",
        "visa_sponsorship": "Not Specified",
        "key_skills": [],
        "benefits": [],
        "industry": [],
        "notes": ""
    }
    
    # Apply defaults for missing fields
    for key, default_value in defaults.items():
        if key not in job_data or job_data[key] is None:
            job_data[key] = default_value

    # Ensure all text fields are strings, not arrays
    text_fields = [
        "job_title", "company_name", "job_id", "work_mode", "timeline",
        "required_education", "required_experience", "salary_range", "visa_sponsorship"
    ]
    
    for field in text_fields:
        if isinstance(job_data.get(field), list):
            job_data[field] = ". ".join(job_data[field])
    
    # Ensure locations is a list and handle empty or None values
    locations = job_data.get("locations", [])
    if locations is None:
        job_data["locations"] = ["Not Specified"]
    elif isinstance(locations, str):
        job_data["locations"] = [loc.strip() for loc in locations.split(",")]
    elif not isinstance(locations, list):
        job_data["locations"] = ["Not Specified"]
    
    # Ensure key_skills is a list
    if isinstance(job_data.get("key_skills"), str):
        job_data["key_skills"] = [skill.strip() for skill in job_data["key_skills"].split(",")]
    elif job_data.get("key_skills") is None:
        job_data["key_skills"] = []
    
    # Handle company size
    valid_sizes = [
        "Startup (<50)",
        "Small (50-200)", 
        "Medium (201-1000)",
        "Large (1000+)",
        "Not Specified"
    ]
    
    company_size = job_data.get('company_size', 'Not Specified')
    if company_size not in valid_sizes:
        # Try to map numeric values
        try:
            size_num = int(''.join(filter(str.isdigit, company_size)))
            if size_num < 50:
                company_size = "Startup (<50)"
            elif size_num <= 200:
                company_size = "Small (50-200)"
            elif size_num <= 1000:
                company_size = "Medium (201-1000)"
            else:
                company_size = "Large (1000+)"
        except:
            company_size = "Not Specified"
    
    job_data['company_size'] = company_size
    return job_data

def parse_job_posting(job_text: str, source: str = None) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Base prompt with JSON instruction
    base_prompt = """You are a job posting analyzer. Extract and return the following information in JSON format:
    - job_title (string)
    - company_name (string)
    - locations (array of strings)
    - work_mode (string: "Remote", "Hybrid", "On-site", or "Not Specified")
    - timeline (string)
    - required_education (string)
    - required_experience (string)
    - key_skills (array of strings)
    - salary_range (string)
    - visa_sponsorship (string: "Yes", "No", or "Not Specified")
    - benefits (array of strings)
    - industry (array of strings)
    - notes (string)
    
    Format your response as a valid JSON object."""

    # Add source-specific instructions
    source_prompts = {
        "pdf": """This text comes from a PDF. Pay special attention to:
        - Section headers that might indicate different parts of the job posting
        - Any formatting artifacts that might need cleaning
        - Tables or structured data that might have been converted to text
        Return the extracted information in JSON format.""",
        
        "linkedin": """This is from LinkedIn. Look for:
        - "About the job" section
        - "About the company" section
        - Skills section with endorsements
        - Experience level indicators
        Return the extracted information in JSON format.""",
        
        "workday": """This is from Workday. Focus on:
        - Job requisition details
        - Qualification sections
        - Basic/Additional qualifications
        - Position details
        Return the extracted information in JSON format.""",
        
        "greenhouse": """This is from Greenhouse. Parse:
        - "What you'll do" section
        - "Who you are" section
        - "About us" section
        - Requirements vs. Nice-to-have skills
        Return the extracted information in JSON format."""
    }

    # Combine prompts
    system_prompt = base_prompt
    if source and source in source_prompts:
        system_prompt += "\n\n" + source_prompts[source]

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this job posting and return a JSON object:\n\n{job_text}"}
            ],
            temperature=0.7
        )
        
        parsed_data = json.loads(response.choices[0].message.content)
        return clean_job_data(parsed_data)
        
    except Exception as e:
        print(f"Error parsing job posting: {str(e)}")
        return None

def main():
    print("Paste the job posting text (press Ctrl+D or Enter twice to finish):")
    job_text = []
    try:
        while True:
            line = input()
            if line == "":
                break
            job_text.append(line)
    except EOFError:
        pass
    
    job_text = "\n".join(job_text)
    
    if not job_text.strip():
        print("No job text provided!")
        return
        
    print("\nParsing job posting...")
    job_data = parse_job_posting(job_text)
    
    if job_data:
        filename = f"hologic_intern.json"
        filepath = os.path.join("job_data", "parsed_jobs", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(job_data, indent=4, fp=f)
        
        print(f"\n✅ Job data saved to {filepath}")
        print("\nYou can now add this job to Notion by running:")
        print(f"python job_tracker.py {filepath}")

if __name__ == "__main__":
    main() 
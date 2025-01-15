from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def clean_job_data(job_data: dict) -> dict:
    # Ensure all text fields are strings, not arrays
    text_fields = [
        "job_title", "company_name", "job_id", "work_mode", "timeline",
        "required_education", "required_experience", "salary_range", "visa_sponsorship"
    ]
    
    for field in text_fields:
        if isinstance(job_data.get(field), list):
            job_data[field] = ". ".join(job_data[field])
    
    # Ensure locations is a list
    if isinstance(job_data.get("locations"), str):
        job_data["locations"] = [job_data["locations"]]
    
    # Ensure key_skills is a list
    if isinstance(job_data.get("key_skills"), str):
        job_data["key_skills"] = [skill.strip() for skill in job_data["key_skills"].split(",")]
    
    return job_data

def parse_job_posting(job_text: str) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    system_prompt = """You are a job posting analyzer. Extract the following information from job postings:
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
    - benefits (array of strings) - Include all mentioned benefits like healthcare, PTO, 401k, etc.
    - industry (array of strings) - The industry sectors this company operates in
    - notes (string) - Any important additional information like: growth opportunities, company culture, special requirements"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": job_text}
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
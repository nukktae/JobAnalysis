from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

class JobSiteExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def extract_linkedin(self, url):
        raise Exception("LinkedIn requires authentication")

    def extract_indeed(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job details
        title = soup.find('h1', {'class': 'jobsearch-JobInfoHeader-title'})
        company = soup.find('div', {'class': 'jobsearch-CompanyInfoContainer'})
        description = soup.find('div', {'id': 'jobDescriptionText'})
        
        job_text = "\n".join([
            title.get_text() if title else "",
            company.get_text() if company else "",
            description.get_text() if description else ""
        ])
        
        return job_text

    def extract_greenhouse(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Set longer timeouts and wait for load
                page.set_default_timeout(60000)  # Increased timeout
                page.set_default_navigation_timeout(60000)
                
                # Navigate and wait for load with retry
                for _ in range(3):  # Try up to 3 times
                    try:
                        page.goto(url, wait_until='networkidle', timeout=30000)
                        break
                    except:
                        time.sleep(2)
                
                # Updated Greenhouse selectors for Base Power Company
                selectors = [
                    '#app div[class^="job-board"]',  # New Base Power selector
                    '#main #content',
                    '#app div[class*="job-content"]',
                    '#app div[class*="posting-content"]',
                    'div[id*="job-content"]',
                    'div[class*="job-content"]',
                    'div[class*="posting"]'
                ]
                
                # Try each selector
                description = None
                for selector in selectors:
                    try:
                        element = page.wait_for_selector(selector, timeout=5000)
                        if element:
                            description = element
                            break
                    except:
                        continue
                
                if not description:
                    # Fallback to getting all main content
                    description = page.query_selector('main') or page.query_selector('#main')
                
                if not description:
                    raise Exception("Could not find job description content")
                
                # Get title and company if available
                title = page.query_selector('h1') or \
                       page.query_selector('.app-title') or \
                       page.query_selector('div[class*="job-title"]')
                
                company = page.query_selector('.company-name') or \
                         page.query_selector('div[class*="company-info"]')
                
                job_text = "\n".join([
                    f"Title: {title.inner_text() if title else ''}",
                    f"Company: {company.inner_text() if company else ''}",
                    f"Description: {description.inner_text()}"
                ])
                
                return job_text.strip()
                
            except Exception as e:
                print(f"Greenhouse extraction error: {str(e)}")
                # Take debug screenshot
                try:
                    page.screenshot(path="greenhouse_error.png")
                except:
                    pass
                raise Exception(f"Failed to extract Greenhouse job content: {str(e)}")
                
            finally:
                page.close()
                context.close()
                browser.close()

    def extract_workday(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Increase timeout and wait for network idle
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Wait for the content to load
                page.wait_for_load_state('networkidle')
                page.wait_for_load_state('domcontentloaded')
                
                # Try multiple possible selectors with increased timeout
                selectors = [
                    '[data-automation-id="jobPostingTitle"]',
                    '[data-automation-id="jobTitle"]',
                    'h2[data-automation-id="jobPostingHeader"]',
                    '.css-1vmnjpn',  # BorgWarner specific class
                    '.css-1q4vxyr',  # Another common Workday class
                    '.css-fqd1kw'    # Another possible title class
                ]
                
                # Wait for any of the title selectors
                title_element = None
                for selector in selectors:
                    try:
                        title_element = page.wait_for_selector(selector, timeout=10000)
                        if title_element:
                            break
                    except:
                        continue
                
                if not title_element:
                    # Try getting all text content if specific selectors fail
                    main_content = page.query_selector('.css-1q4vxyr') or \
                                 page.query_selector('.css-fqd1kw') or \
                                 page.query_selector('main')
                    
                    if main_content:
                        return main_content.inner_text()
                    raise Exception("Could not find any job content")
                
                # Extract job details with multiple selector attempts
                description = page.query_selector('[data-automation-id="jobPostingDescription"]') or \
                             page.query_selector('.css-m9i0qw') or \
                             page.query_selector('[data-automation-id="job_posting_description"]')
                             
                location = page.query_selector('[data-automation-id="jobPostingLocation"]') or \
                          page.query_selector('[data-automation-id="location"]') or \
                          page.query_selector('.css-1sg2lsz')
                
                # Additional job details
                company = page.query_selector('[data-automation-id="companyTitle"]') or \
                         page.query_selector('.css-1h46us9')
                         
                requirements = page.query_selector('[data-automation-id="jobPostingRequirements"]') or \
                              page.query_selector('[data-automation-id="job_posting_requirements"]')
                
                job_text = "\n".join([
                    f"Title: {title_element.inner_text() if title_element else ''}",
                    f"Company: {company.inner_text() if company else ''}",
                    f"Location: {location.inner_text() if location else ''}",
                    f"Description: {description.inner_text() if description else ''}",
                    f"Requirements: {requirements.inner_text() if requirements else ''}"
                ])
                
                return job_text.strip()
                
            except Exception as e:
                print(f"Detailed Workday extraction error: {str(e)}")
                # Take a screenshot for debugging
                page.screenshot(path="error_screenshot.png")
                return None
            finally:
                browser.close()

    def extract_generic(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
            
        return soup.get_text(separator='\n', strip=True) 

    def extract_with_playwright(self, url):
        browser = None
        context = None
        page = None
        
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Set longer timeouts and wait for full page load
            page.set_default_timeout(60000)  # 60 seconds
            page.set_default_navigation_timeout(60000)
            
            # Navigate and wait for network idle and DOM content
            response = page.goto(url, wait_until='domcontentloaded')
            if not response:
                raise Exception("Failed to load the page")
            
            # Wait for network to be idle and page to stabilize
            page.wait_for_load_state('networkidle')
            
            # Specific handling for Greenhouse
            if 'greenhouse.io' in url:
                try:
                    # Wait for job content with longer timeout
                    content = page.wait_for_selector('.content', timeout=30000)
                    if content:
                        job_description = page.query_selector('#content')
                        if job_description:
                            return job_description.inner_text()
                        
                    # Fallback selectors for Greenhouse
                    selectors = [
                        '#content',
                        '#app-container',
                        '.main-content',
                        '[data-test="description"]',
                        '.job-content'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = page.wait_for_selector(selector, timeout=5000)
                            if element:
                                return element.inner_text()
                        except:
                            continue
                            
                    # If no specific selector works, try getting all main content
                    main_content = page.query_selector('main')
                    if main_content:
                        return main_content.inner_text()
                        
                except Exception as e:
                    print(f"Greenhouse specific error: {str(e)}")
                    # Take debug screenshot
                    page.screenshot(path="greenhouse_error.png")
                    raise Exception("Failed to extract Greenhouse job content")
            
            # Try multiple selectors for job content
            selectors = [
                'div[class*="job-description"]',
                'div[class*="description"]',
                'div[class*="posting"]',
                'div[class*="content"]',
                'main'
            ]
            
            content_element = None
            for selector in selectors:
                try:
                    content_element = page.wait_for_selector(selector, timeout=5000)
                    if content_element:
                        break
                except:
                    continue
            
            if not content_element:
                raise Exception("Could not find job content")
            
            # Extract job details with multiple selector attempts
            title = page.query_selector('h1') or \
                    page.query_selector('h2') or \
                    page.query_selector('.job-title')
                    
            company = page.query_selector('div[class*="company-name"]') or \
                     page.query_selector('div[class*="company"]') or \
                     page.query_selector('.organization-name')
                     
            description = content_element
            
            # Ensure we have content before closing browser
            job_text = "\n".join([
                f"Title: {title.inner_text() if title else ''}",
                f"Company: {company.inner_text() if company else ''}",
                f"Description: {description.inner_text() if description else ''}"
            ])
            
            if not job_text.strip():
                raise Exception("No content extracted")
                
            return job_text.strip()
            
        except Exception as e:
            print(f"Playwright extraction error: {str(e)}")
            try:
                if page and not page.is_closed():
                    os.makedirs("debug_screenshots", exist_ok=True)
                    screenshot_path = f"debug_screenshots/error_{int(time.time())}.png"
                    page.screenshot(path=screenshot_path)
                    print(f"Debug screenshot saved to: {screenshot_path}")
            except Exception as screenshot_error:
                print(f"Failed to take screenshot: {str(screenshot_error)}")
            return None
            
        finally:
            try:
                if page:
                    page.close()
                if context:
                    context.close()
                if browser:
                    browser.close()
                if 'playwright' in locals():
                    playwright.stop()
            except Exception as cleanup_error:
                print(f"Cleanup error: {str(cleanup_error)}") 

    def extract_brassring(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Set longer timeouts and wait for load
                page.set_default_timeout(60000)  # 60 seconds
                page.set_default_navigation_timeout(60000)
                
                # Navigate and wait for load with retry
                for _ in range(3):  # Try up to 3 times
                    try:
                        page.goto(url, wait_until='networkidle', timeout=30000)
                        break
                    except:
                        time.sleep(2)
                
                # Wait for job details to load
                page.wait_for_selector('div#job-details, div#jobDetails', timeout=30000)
                
                # Brassring specific selectors
                selectors = [
                    'div#job-details',
                    'div#jobDetails',
                    'div.job-details',
                    'div.jobdetail',
                    'div[class*="job-description"]',
                    'div[class*="description"]'
                ]
                
                # Try each selector
                content = None
                for selector in selectors:
                    try:
                        element = page.wait_for_selector(selector, timeout=5000)
                        if element:
                            content = element
                            break
                    except:
                        continue
                
                if not content:
                    # Fallback to getting all main content
                    content = page.query_selector('main') or page.query_selector('body')
                
                if not content:
                    raise Exception("Could not find job description content")
                
                # Get title and company if available
                title = page.query_selector('h1.job-title') or \
                       page.query_selector('h1') or \
                       page.query_selector('.jobtitle')
                
                company = page.query_selector('.company-name') or \
                         page.query_selector('.organization-name') or \
                         page.query_selector('div[class*="company"]')
                
                job_text = "\n".join([
                    f"Title: {title.inner_text() if title else ''}",
                    f"Company: {company.inner_text() if company else ''}",
                    f"Description: {content.inner_text()}"
                ])
                
                return job_text.strip()
                
            except Exception as e:
                print(f"Brassring extraction error: {str(e)}")
                try:
                    os.makedirs("debug_screenshots", exist_ok=True)
                    screenshot_path = f"debug_screenshots/brassring_error_{int(time.time())}.png"
                    page.screenshot(path=screenshot_path)
                    print(f"Debug screenshot saved to: {screenshot_path}")
                except:
                    pass
                raise Exception(f"Failed to extract Brassring job content: {str(e)}")
                
            finally:
                page.close()
                context.close()
                browser.close() 
import os
import re
import time
import json
import urllib.parse
import pandas as pd
import requests
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
INPUT_FILE = "ad_campaign_list.xlsx"      # Your input Excel file name
OUTPUT_FILE = "qa_results_report.xlsx"     # Output report name
TIMEOUT_SECONDS = 15                       # Timeout for page loads

# --- UTILITY FUNCTIONS ---
def clean_and_normalize_text(text):
    """Normalize text by converting to lowercase and removing punctuation/spaces."""
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def normalize_url(url_str):
    """Normalize URL by extracting only domain and path, ignoring protocol, tracking params, and trailing slashes."""
    if not url_str:
        return ""
    # Ensure URL has protocol for urlparse to succeed
    if not url_str.startswith(('http://', 'https://')):
        url_str = 'https://' + url_str
    parsed = urllib.parse.urlparse(url_str)
    domain = parsed.netloc.lower().replace('www.', '')
    path = parsed.path.lower().rstrip('/')
    return f"{domain}{path}"

def fetch_json_feed(feed_url):
    """Fetch and parse feed JSON data."""
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[-] Error fetching JSON from {feed_url}: {e}")
        return None

# --- CORE QA FUNCTION ---
def run_qa():
    # Load input data
    if not os.path.exists(INPUT_FILE):
        print(f"[-] Input file '{INPUT_FILE}' not found! Please check the path.")
        return
    
    df = pd.read_excel(INPUT_FILE)
    
    # Standardize column names (handles casing or spaces)
    df.columns = [col.strip() for col in df.columns]
    
    # Initialize result columns
    results = []

    print("[+] Initializing browser for ad preview testing...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False if you want to watch it work
        
        for index, row in df.iterrows():
            version_name = row.get("Version Name") or row.get("Name")
            feed_url = row.get("feedEndpoint")
            preview_url = row.get("preview") or row.get("Preview")
            
            print(f"\n[+] Processing Row {index + 1}: {version_name}")
            
            # Record base metrics
            row_result = {
                "Version Name": version_name,
                "Feed Endpoint": feed_url,
                "Preview Link": preview_url,
                "Expected City": "N/A",
                "Expected URL": "N/A",
                "Actual Redirect URL": "N/A",
                "Text Check Status": "FAILED",
                "Redirect Check Status": "FAILED",
                "QA Status": "FAILED",
                "Notes": ""
            }
            
            # Step 1: Fetch and parse JSON Data
            feed_data = fetch_json_feed(feed_url)
            if not feed_data:
                row_result["Notes"] = "Failed to fetch or parse JSON feed."
                results.append(row_result)
                continue
            
            # Extract target variables (supports lists/dicts)
            if isinstance(feed_data, list) and len(feed_data) > 0:
                # If feed is a list of routes, find first or matching element
                feed_item = feed_data[0] 
            else:
                feed_item = feed_data
                
            expected_city = feed_item.get("destination_city_name")
            expected_url = feed_item.get("url")
            
            row_result["Expected City"] = expected_city
            row_result["Expected URL"] = expected_url
            
            if not expected_city or not expected_url:
                row_result["Notes"] = "Could not locate 'destination_city_name' or 'url' in JSON feed."
                results.append(row_result)
                continue
            
            # Step 2: Open ad preview and verify text
            try:
                page = browser.new_page()
                page.goto(preview_url, timeout=TIMEOUT_SECONDS * 1000)
                page.wait_for_load_state("networkidle")
                
                # Extract text content of main page and all nested iframes
                page_texts = [page.locator("body").text_content() or ""]
                for frame in page.frames:
                    try:
                        iframe_text = frame.locator("body").text_content()
                        if iframe_text:
                            page_texts.append(iframe_text)
                    except Exception:
                        pass
                
                # Check for city text presence (normalized to prevent punctuation/spacing mismatches)
                normalized_expected_city = clean_and_normalize_text(expected_city)
                text_match_found = False
                for raw_text in page_texts:
                    if normalized_expected_city in clean_and_normalize_text(raw_text):
                        text_match_found = True
                        break
                
                if text_match_found:
                    row_result["Text Check Status"] = "PASSED"
                else:
                    row_result["Notes"] += f"City '{expected_city}' not found in ad text. "
                
                # Step 3: Click the ad to test destination URL redirection
                actual_redirect_url = ""
                try:
                    # Expect a new tab/popup window when we click
                    with page.expect_popup(timeout=8000) as popup_info:
                        # Find the ad iframe (usually the first child iframe on the preview page)
                        ad_frame = None
                        for frame in page.frames:
                            if frame != page.main_frame:
                                ad_frame = frame
                                break
                        
                        # Click on the iframe body or main body of the page to trigger the click-through
                        if ad_frame:
                            ad_frame.locator("body").click()
                        else:
                            page.locator("body").click()
                    
                    popup_page = popup_info.value
                    popup_page.wait_for_load_state("domcontentloaded")
                    actual_redirect_url = popup_page.url
                    actual_redirect_url = actual_redirect_url.replace("%2F", "/")
                    actual_redirect_url = actual_redirect_url.replace("https://creativepreview.flashtalking.net/clicktag/2/?count=2&APPEND=true&DYNCTTEST=", "")
                    popup_page.close()
                    
                except Exception as click_err:
                    row_result["Notes"] += f"Redirect click failed: {click_err}. "
                
                # Step 4: Compare Redirect URL
                if actual_redirect_url:
                    row_result["Actual Redirect URL"] = actual_redirect_url
                    norm_expected_url = normalize_url(expected_url)
                    norm_actual_url = normalize_url(actual_redirect_url)
                    
                    if norm_expected_url in norm_actual_url or norm_actual_url in norm_expected_url:
                        row_result["Redirect Check Status"] = "PASSED"
                    else:
                        row_result["Notes"] += f"URL mismatch. Expected: {expected_url} | Got: {actual_redirect_url}"
                
                page.close()
                
            except Exception as page_err:
                row_result["Notes"] += f"Browser navigation error: {page_err}"
            
            # Determine Final Status
            if row_result["Text Check Status"] == "PASSED" and row_result["Redirect Check Status"] == "PASSED":
                row_result["QA Status"] = "PASSED"
                row_result["Notes"] = "All checks passed successfully."
                
            results.append(row_result)
        
        browser.close()
        
    # Write report back to Excel
    report_df = pd.DataFrame(results)
    report_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n[+] QA Run Complete! Results saved to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    run_qa()
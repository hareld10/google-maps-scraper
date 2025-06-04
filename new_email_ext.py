import re
import time
import json
import pandas as pd
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed

from urllib.parse import urlparse
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Create data directory if it doesn't exist
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)


def normalize_url(website):
    if any(domain in website.lower() for domain in ["facebook.com", "instagram.com", "tripadvisor.com", "wolt.com"]):
        return None
    if not website or not isinstance(website, str):
        return None
    website = website.strip()
    parsed = urlparse(website)
    if not parsed.scheme:
        website = "https://" + website
    return website


def find_email_in_text(text):
    emails = re.findall(EMAIL_REGEX, text)
    return emails[0] if emails else None


def get_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    return webdriver.Chrome(options=options)


def extract_email_from_website(website):
    website = normalize_url(website)

    if website == None:
        return None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(15)

        # Try common contact page paths
        contact_paths = ['/contact', '/contact-us', '/kontakt']
        for path in contact_paths:
            try:
                driver.get(website.rstrip('/') + path)
                time.sleep(2)
                text = driver.find_element(By.TAG_NAME, 'body').text
                email = find_email_in_text(text)
                if email:
                    return email
            except WebDriverException:
                continue

        # Fallback: visit homepage
        driver.get(website)
        time.sleep(3)

        # Scroll to load lazy content
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        text = driver.find_element(By.TAG_NAME, 'body').text
        return find_email_in_text(text)
    except Exception as e:
        print(f"Error while processing {website}: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass


# Batch mode using Excel
def batch_process_from_excel(excel_file):
    # Check if Excel file exists
    print("in batch_process_from_excel")
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Excel file not found: {excel_file}")

    print(f"📊 Loading data from {excel_file}")
    df = pd.read_excel(excel_file)
    
    total_websites = len(df[pd.notna(df['Website'])])
    print(f"🔍 Found {total_websites} websites to process")
    
    processed = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {
            executor.submit(extract_email_from_website, row['Website']): index
            for index, row in df.iterrows()
            if pd.notna(row['Website'])
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            website = df.at[idx, 'Website']
            try:
                email = future.result()
                df.at[idx, 'Email'] = email
                processed += 1
                print(f"[{processed}/{total_websites}] {'✔️ Found' if email else '❌ No'} email on {website}: {email or 'N/A'}")
            except Exception as e:
                print(f"❌ Error on {website}: {e}")
                df.at[idx, 'Email'] = 'ERROR: ' + str(e)

    output_file = os.path.join(DATA_DIR, os.path.basename(excel_file).replace(".xlsx", "_updated.xlsx"))
    df.to_excel(output_file, index=False)
    print(f"\n✅ Done. Results saved to: {output_file}")
    print(f"📊 Summary: Processed {processed} websites")


def run_on_data_dir():
    for file in os.listdir(DATA_DIR):
        if file.endswith(".xlsx"):
            print(f"📊 Processing {file}")
            batch_process_from_excel(os.path.join(DATA_DIR, file))  

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Extract emails from websites listed in Excel file')
        parser.add_argument('--excel', required=True, help='Path to Excel file')
        args = parser.parse_args()
        
        batch_process_from_excel(args.excel)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        exit(1)

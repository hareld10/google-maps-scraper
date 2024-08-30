import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException

def find_email_in_text(text):
    '''
    Regex pattern to match most email addresses
    '''
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def check_contact_page(driver, base_url):
    '''
    Check contant page to see if there are any emails
    '''
    contact_url = f"{base_url}/contact"
    driver.get(contact_url)
    time.sleep(3)
    
    try:
        # Extract the page's text content
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        email = find_email_in_text(page_text)
        return email if email else None
    except NoSuchElementException:
        return None

def process_website(website):
    '''
    Initiate Selenium Webdriver
    '''
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)

    email = None
    try:
        # Check if there is a /contact page
        email = check_contact_page(driver, website)
        
        if not email:
            driver.get(website)
            time.sleep(3)

            # Scroll to the bottom of the page
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Extract the page's text content
            page_text = driver.find_element(By.TAG_NAME, 'body').text

            # Search for an email in the page's text
            email = find_email_in_text(page_text)
        return email if email else None

    except Exception as e:
        print(f"An error occurred while processing {website}: {e}")
        return None
    finally:
        driver.quit()

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

excel_file = config['excel_file']

df = pd.read_excel(excel_file)

with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_website = {executor.submit(process_website, row['Website']): index for index, row in df.iterrows() if not pd.isna(row['Website'])}

    for future in as_completed(future_to_website):
        index = future_to_website[future]
        website = df.at[index, 'Website']
        
        try:
            email = future.result()
            if email:
                df.at[index, 'Email'] = email
                print(f"Found email: {email} on {website}")
            else:
                print(f"No email found on {website}")
        except Exception as e:
            print(f"Error processing {website}: {e}")

# Save the updated Excel file
updated_file = excel_file.replace('.xlsx', '_updated.xlsx')
df.to_excel(updated_file, index=False)

print(f"Script completed. All websites have been checked and the Excel file is updated: {updated_file}")

import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import json

# Setup and initial configurations
URL = "https://www.google.com/maps"
service = "ENTER A SERVICE OR A NAME"  # e.g. catering, events, etc. OR starbucks, mcdonalds, etc.
location = "ENTER LOCATION"  # e.g. London, Germany, etc.

print("Starting the web scraping script...")

options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
print(f"Accessing URL: {URL}")
driver.get(URL)

# Accept cookies
try:
    print("Looking for accept cookies button...")
    accept_cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button')))
    accept_cookies.click()
    print("Accepted cookies.")
except NoSuchElementException:
    print("No accept cookies button found.")

# Search for results
print(f"Searching for: {service} in {location}")
input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchboxinput"]')))
input_field.send_keys(service.lower() + ' ' + location.lower())
input_field.send_keys(Keys.ENTER)
print("Search submitted.")

# Wait for the sidebar to load
print("Waiting for the sidebar to load...")
divSideBar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[aria-label*='{service.lower()} {location.lower()}']")))

# Scroll through the results
print("Scrolling the sidebar to load all of the results...")
previous_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)
while True:
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", divSideBar)
    time.sleep(3)
    new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", divSideBar)
    if new_scroll_height == previous_scroll_height:
        break
    previous_scroll_height = new_scroll_height
print("Finished scrolling.")

# Parse the page source
print("Parsing the page source...")
page_source = driver.page_source
driver.quit()

soup = BeautifulSoup(page_source, "html.parser")
boxes = soup.find_all('div', class_='Nv2PK')

# Collect data
print("Collecting data...")
data = []

for box in boxes:
    # Business name
    try:
        business_name = box.find('div', class_='qBF1Pd').getText()
    except AttributeError:
        business_name = "N/A"

    # Address
    try:
        inner_div = box.find_all('div', class_='W4Efsd')[1].find('div', class_='W4Efsd')
        address = [span.text for span in inner_div.find_all('span') if span.text and not span.find('span')][-1]
    except (IndexError, AttributeError):
        address = "N/A"

    # Stars
    try:
        stars = box.find('span', class_='MW4etd').getText()
    except AttributeError:
        stars = "N/A"

    # Number of reviews
    try:
        number_of_reviews = box.find('span', class_='UY7F9').getText().strip('()')
    except AttributeError:
        number_of_reviews = "N/A"

    # Phone number
    try:
        phone_number = box.find('span', class_='UsdlK').getText()
    except AttributeError:
        phone_number = "N/A"

    # Website
    try:
        website = box.find('a', class_='lcr4fd').get('href')
    except AttributeError:
        website = "N/A"

    # Append to data list
    data.append({
        'Business Name': business_name,
        'Address': address,
        'Stars': stars,
        'Number of Reviews': number_of_reviews,
        'Phone Number': phone_number,
        'Website': website,
        'Email': ' ',
    })

# Create a DataFrame and save to Excel
excel_file = f'{location}_{service}.xlsx'
df = pd.DataFrame(data)
df.to_excel(excel_file, index=False)

print(f"Data has been saved to {excel_file}")

# Create a configuration file
config = {
    'excel_file': excel_file
}
with open('config.json', 'w') as config_file:
    json.dump(config, config_file)
print("Configuration file created: config.json")

# Call the email extraction script
print("Calling the email extraction script...")
subprocess.run(['python', 'email_extraction_script.py'])
print("Email extraction script completed.")

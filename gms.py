import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import json
import os

# Create data directory if it doesn't exist
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def scrape_location(location, service="restaurants"):
    """
    Scrape Google Maps data for a specific location and service type.
    
    Args:
        location (str): The location to search for
        service (str): The type of service to search for (default: restaurants)
    
    Returns:
        str: Path to the generated Excel file
    """
    print(f"\nScraping {service} in {location}...")
    
    URL = f"https://www.google.com/maps/search/{service.replace(' ', '+')}+{location.replace(' ', '+')}/?hl=en"

    options = Options()
    options.add_argument("--lang=en")  # force English UI
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    # Wait for the sidebar to load
    print("Waiting for the sidebar to load...")
    sidebar = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
    )

    # Scroll through the results
    print("Scrolling the sidebar to load all of the results...")
    prev_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
        if new_height == prev_height:
            break
        prev_height = new_height
    print("Finished scrolling.")

    # Collect data
    data = []
    boxes = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    count = len(boxes)
    print(f"Found {count} results, extracting details...")

    for idx in range(count):
        boxes = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
        box = boxes[idx]

        # Parse static info with BeautifulSoup
        html = box.get_attribute("outerHTML")
        mini = BeautifulSoup(html, "html.parser")
        name = mini.find('div', class_='qBF1Pd').get_text(strip=True) if mini.find('div', 'qBF1Pd') else "N/A"
        stars = mini.find('span', class_='c').get_text(strip=True) if mini.find('span', 'c') else "N/A"
        reviews = mini.find('span', class_='UY7F9').get_text(strip=True).strip("()") if mini.find('span', 'UY7F9') else "N/A"
        addr = " / ".join(span.get_text(strip=True) for span in mini.select("div.W4Efsd span") if span.get_text(strip=True)) or "N/A"

        # Click the listing to open detail pane
        link = box.find_element(By.TAG_NAME, "a")
        driver.execute_script("arguments[0].click();", link)

        # Wait for the detail pane to show the correct name
        try:
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "DUwDvf"), name)
            )
        except TimeoutException:
            print(f"⚠️ Timeout waiting for detail pane for {name}")

        time.sleep(1.5)  # let rest of details load

        # Extract Website
        try:
            website_el = driver.find_element(By.CSS_SELECTOR, "[aria-label^='Website']")
            website = website_el.get_attribute("aria-label").split("Website:")[-1].strip()
        except:
            website = "N/A"

        # Extract Phone
        try:
            phone_el = driver.find_element(By.CSS_SELECTOR, "[aria-label^='Phone']")
            phone = phone_el.get_attribute("aria-label").split("Phone:")[-1].strip()
        except:
            phone = "N/A"

        # Go back to list view
        try:
            back_btn = driver.find_element(By.CSS_SELECTOR, "button[jsaction='pane.homeBack']")
            back_btn.click()
        except:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        data.append({
            'Business Name': name,
            'Address': addr,
            'Stars': stars,
            'Number of Reviews': reviews,
            'Phone Number': phone,
            'Website': website,
            'Email': '',
        })

        time.sleep(1)

    # Save to Excel
    excel_file = os.path.join(DATA_DIR, f'{location.replace(" ", "_")}_{service}.xlsx')
    pd.DataFrame(data).to_excel(excel_file, index=False)
    print(f"✅ Data has been saved to {excel_file}")

    # Call email extraction script
    print("📨 Calling the email extraction script...")
    try:
        result = subprocess.run(['python', 'new_email_ext.py', '--excel', excel_file], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("⚠️ Email extraction warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("❌ Email extraction script failed:", e)
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print("❌ Could not find new_email_ext.py")
    else:
        print("✅ Email extraction script completed successfully.")

    # Close browser
    driver.quit()
    
    return excel_file

if __name__ == "__main__":
    # For backward compatibility when running directly
    scrape_location("patong beach")
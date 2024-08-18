import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Function to extract email addresses from a webpage's content
def find_email_in_text(text):
    # Regex pattern to match most email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

# Load the Excel file
df = pd.read_excel('results/stoke-on-trent_catering.xlsx')

# Initialize the WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

# Loop through each row in the Excel file
for index, row in df.iterrows():
    website = row['Website']

    # Skip rows with missing or empty website
    if pd.isna(website) or website.strip() == "":
        print(f"No website found for row {index + 1}, skipping...")
        continue

    # Check if the email column is empty
    if pd.isna(row['Email']):
        try:
            # Open the website
            driver.get(website)
            time.sleep(3)  # Wait for the page to load fully

            # Scroll to the bottom of the page
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down to the bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new content to load

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Extract the page's text content
            page_text = driver.find_element(By.TAG_NAME, 'body').text

            # Search for an email in the page's text
            email = find_email_in_text(page_text)

            # If an email is found, save it to the dataframe
            if email:
                df.at[index, 'Email'] = email
                print(f"Found email: {email} on {website}")
            else:
                print(f"No email found on {website}")

        except Exception as e:
            print(f"Error accessing {website} for row {index + 1}: {e}")

# Save the updated Excel file
df.to_excel('results_with_email/stoke-on-trent_catering.xlsx', index=False)

# Keep the browser open until the loop is done
driver.quit()

print("Script completed. All websites have been checked and the Excel file is updated.")

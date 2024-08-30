# Google Maps Scraper

This repository contains two Python scripts designed to scrape business data from Google Maps and extract email addresses from the collected websites.

## Overview

1. **Web Scraping Script:** `google_maps_scraper.py` scrapes business data from Google Maps based on a specified service and location and saves this data to an Excel file.
2. **Email Extraction Script:** `email_extraction_script.py` reads the generated Excel file, visits each business website, and extracts email addresses, saving the results to a new Excel file.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/FraneCal/google-maps-scraper.git
    cd google-maps-scraper
    ```

2. **Install required Python packages:**

    Create a `requirements.txt` file with the following content:

    ```
    selenium==4.16.1
    pandas==2.0.2
    beautifulsoup4==4.12.2
    ```

    Install the packages using:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Update the Web Scraping Script:**

    Open `google_maps_scraper.py` and modify the following variables:

    ```python
    service = "ENTER SERVICE OR PLACE"  # e.g. catering, events, etc. OR starbucks, mcdonalds, etc.
    location = "ENTER LOCATION"  # e.g. London, Germany, etc.
    ```

2. **Run the Web Scraping Script:**

    Execute the script with:

    ```bash
    python google_maps_scraper.py
    ```

    This script will generate an Excel file named `location_service.xlsx` and a `config.json` file containing the name of the generated Excel file.

    After that, the script will call `email_extraction_script.py` script.

    This script will read the Excel file specified in `config.json`, extract emails from each business website, and save the results to a new Excel file with `_updated` appended to the original filename.

## Notes

- Ensure that Google Chrome and ChromeDriver versions are compatible.
- Modify the paths and URLs in the scripts as needed for different environments.
- The scripts use `--headless` mode for ChromeDriver, which means they run without opening a visible browser window. Remove this option if you want to see the browser interactions.

## Contributing

Feel free to open issues or submit pull requests if you find bugs or have improvements to suggest.

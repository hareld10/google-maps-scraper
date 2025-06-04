import argparse
import json
import pandas as pd
import time
from gms import scrape_location

def scrape_multiple_locations(locations, service="restaurants"):
    """
    Scrape Google Maps data for multiple locations.
    
    Args:
        locations (list): List of location names to scrape
        service (str): Type of service to search for (default: restaurants)
    """
    results = []
    
    print(f"Starting scraping for {len(locations)} locations...")
    
    for location in locations:
        try:
            excel_file = scrape_location(location, service)
            results.append({
                'location': location,
                'status': 'success',
                'file': excel_file
            })
        except Exception as e:
            print(f"❌ Error scraping {location}: {str(e)}")
            results.append({
                'location': location,
                'status': 'failed',
                'error': str(e)
            })
        time.sleep(30)
    
    # Save summary report
    summary_file = 'scraping_summary.xlsx'
    pd.DataFrame(results).to_excel(summary_file, index=False)
    print(f"\n✅ Summary report saved to {summary_file}")
    
    # Print final summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\nScraping completed:")
    print(f"- Total locations: {len(locations)}")
    print(f"- Successful: {successful}")
    print(f"- Failed: {len(locations) - successful}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Google Maps data for multiple locations')
    parser.add_argument('--locations', type=str, help='Comma-separated list of locations or path to JSON file with locations array')
    parser.add_argument('--service', type=str, default='restaurants', help='Type of service to search for (default: restaurants)')
    
    args = parser.parse_args()
    
    if args.locations.endswith('.json'):
        # Read locations from JSON file
        with open(args.locations, 'r') as f:
            locations = json.load(f)
            if not isinstance(locations, list):
                raise ValueError("JSON file must contain an array of location strings")
    else:
        # Parse comma-separated locations
        locations = [loc.strip() for loc in args.locations.split(',')]
    
    scrape_multiple_locations(locations, args.service) 
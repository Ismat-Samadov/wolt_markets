#!/usr/bin/env python3
"""
Wolt Markets Scraper - Focused on Baku, Azerbaijan
Scrapes supermarkets, items, prices from Wolt API for Baku
"""

import requests
import json
import csv
import time
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WoltMarketsScraper:
    """Scraper for Wolt Markets data"""

    BASE_URL = "https://restaurant-api.wolt.com"
    CONSUMER_API_URL = "https://consumer-api.wolt.com"

    # Baku, Azerbaijan coordinates
    DEFAULT_LAT = 40.373141313556964
    DEFAULT_LON = 49.84575754727883

    def __init__(self, output_dir: str = "data", target_city: str = "baku"):
        self.output_dir = output_dir
        self.target_city = target_city
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate',  # Exclude br (brotli) to avoid decompression issues
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'app-language': 'az',
            'client-version': '1.16.76',
            'clientversionnumber': '1.16.76',
            'platform': 'Web',
            'origin': 'https://wolt.com',
            'referer': 'https://wolt.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        })

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Data storage
        self.markets = []
        self.items = []

    def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Dict]:
        """Make HTTP request with error handling and rate limiting"""
        try:
            time.sleep(0.5)  # Rate limiting

            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            return None

    def fetch_retail_markets(self, lat: float, lon: float, city_slug: str = "") -> List[Dict]:
        """Fetch retail markets for a specific location"""
        logger.info(f"Fetching retail markets for location: {lat}, {lon}")
        url = f"{self.CONSUMER_API_URL}/v1/pages/retail?lat={lat}&lon={lon}"

        data = self.make_request(url)
        if not data:
            return []

        markets = []
        sections = data.get('sections', [])

        for section in sections:
            items = section.get('items', [])
            for item in items:
                if 'venue' in item:
                    venue = item['venue']
                    venue['city_slug'] = city_slug
                    venue['city_name'] = data.get('city', '')
                    markets.append(venue)

        logger.info(f"Found {len(markets)} markets")
        return markets

    def fetch_venue_details(self, venue_slug: str) -> Optional[Dict]:
        """Fetch detailed information about a specific venue including all items"""
        logger.info(f"Fetching details for venue: {venue_slug}")
        url = f"{self.CONSUMER_API_URL}/consumer-api/venue-content-api/v3/web/venue-content/slug/{venue_slug}"

        data = self.make_request(url)
        if data:
            # Debug logging
            has_items = 'items' in data and len(data.get('items', [])) > 0
            has_sections = 'sections' in data and len(data.get('sections', [])) > 0
            logger.debug(f"Venue {venue_slug}: has_items={has_items}, has_sections={has_sections}")
            if has_items:
                logger.debug(f"Venue {venue_slug}: {len(data.get('items', []))} items found")

        return data

    def extract_items_from_venue(self, venue_data: Dict, venue_info: Dict) -> List[Dict]:
        """Extract all items from venue data"""
        if not venue_data:
            return []

        items = []

        # Get sections - items are directly in each section
        venue_sections = venue_data.get('sections', [])
        if not venue_sections:
            logger.warning(f"No sections found in venue data for {venue_info.get('name', 'unknown')}")
            return []

        for section in venue_sections:
            section_name = section.get('name', '')
            section_slug = section.get('slug', '')

            # Items are directly in the section
            section_items = section.get('items', [])

            for item_data in section_items:
                # Extract comprehensive item information
                item = {
                    'item_id': item_data.get('id', ''),
                    'venue_id': venue_info.get('id', ''),
                    'venue_name': venue_info.get('name', ''),
                    'venue_slug': venue_info.get('slug', ''),
                    'city': venue_info.get('city_name', ''),
                    'city_slug': venue_info.get('city_slug', ''),
                    'section_name': section_name,
                    'section_slug': section_slug,
                    'name': item_data.get('name', ''),
                    'description': item_data.get('description', ''),
                    'price': item_data.get('price', 0) / 100,  # Convert to decimal
                    'original_price': item_data.get('original_price', 0) / 100 if item_data.get('original_price') else None,
                    'discount_amount': (item_data.get('original_price', 0) - item_data.get('price', 0)) / 100 if item_data.get('original_price') else 0,
                    'discount_percentage': round(((item_data.get('original_price', 0) - item_data.get('price', 0)) / item_data.get('original_price', 1)) * 100, 2) if item_data.get('original_price') and item_data.get('original_price') > 0 else 0,
                    'unit_info': item_data.get('unit_info', ''),
                    'unit_price_value': item_data.get('unit_price', {}).get('price', 0) / 100 if item_data.get('unit_price') else None,
                    'unit_price_base': item_data.get('unit_price', {}).get('base', 0) if item_data.get('unit_price') else None,
                    'unit_price_unit': item_data.get('unit_price', {}).get('unit', '') if item_data.get('unit_price') else '',
                    'barcode_gtin': item_data.get('barcode_gtin', ''),
                    'image_url': item_data.get('images', [{}])[0].get('url', '') if item_data.get('images') else '',
                    'image_blurhash': item_data.get('images', [{}])[0].get('blurhash', '') if item_data.get('images') else '',
                    'purchasable_balance': item_data.get('purchasable_balance', None),
                    'quantity_left': item_data.get('quantity_left', None),
                    'max_quantity_per_purchase': item_data.get('max_quantity_per_purchase', None),
                    'min_quantity_per_purchase': item_data.get('min_quantity_per_purchase', None),
                    'alcohol_permille': item_data.get('alcohol_permille', 0),
                    'caffeine_info': item_data.get('caffeine_info', ''),
                    'vat_percentage': item_data.get('vat_percentage', 0),
                    'dietary_preferences': ','.join([pref if isinstance(pref, str) else pref.get('id', '') for pref in item_data.get('dietary_preferences', [])]),
                    'tags': ','.join([tag.get('id', '') if isinstance(tag, dict) else str(tag) for tag in item_data.get('tags', [])]),
                    'is_available': not item_data.get('disabled_info'),
                    'is_wolt_plus_only': item_data.get('is_wolt_plus_only', False),
                    'is_cutlery': item_data.get('is_cutlery', False),
                    'deposit': item_data.get('deposit', None),
                    'scraped_at': datetime.now().isoformat(),
                }

                items.append(item)

        logger.info(f"Extracted {len(items)} items from {venue_info.get('name', 'unknown venue')}")
        return items

    def scrape_markets(self):
        """Main scraping function for target city"""
        logger.info(f"Starting Wolt Markets scraping for {self.target_city}...")

        # Use default Baku coordinates
        lat = self.DEFAULT_LAT
        lon = self.DEFAULT_LON
        city_slug = self.target_city
        city_name = self.target_city.capitalize()

        logger.info(f"Processing city: {city_name} ({city_slug})")

        # Fetch retail markets for this city
        markets = self.fetch_retail_markets(lat, lon, city_slug)

        if not markets:
            logger.error("No markets found for the target city")
            return

        # Process each market
        for market in markets:
            market_slug = market.get('slug', '')
            market_name = market.get('name', '')

            # Add market to our collection
            market_data = {
                'venue_id': market.get('id', ''),
                'name': market_name,
                'slug': market_slug,
                'address': market.get('address', ''),
                'city': city_name,
                'city_slug': city_slug,
                'country': market.get('country', ''),
                'latitude': market.get('location', [0, 0])[1],
                'longitude': market.get('location', [0, 0])[0],
                'rating_score': market.get('rating', {}).get('score', None),
                'rating_volume': market.get('rating', {}).get('volume', None),
                'price_range': market.get('price_range', None),
                'online': market.get('online', False),
                'delivers': market.get('delivers', False),
                'delivery_price': market.get('delivery_price_int', 0) / 100,
                'estimate_minutes': market.get('estimate', 0),
                'estimate_range': market.get('estimate_range', ''),
                'short_description': market.get('short_description', ''),
                'tags': ','.join(market.get('tags', [])),
                'scraped_at': datetime.now().isoformat(),
            }
            self.markets.append(market_data)

            # Fetch detailed venue information including items
            venue_details = self.fetch_venue_details(market_slug)

            if venue_details:
                # Extract all items from this venue
                venue_items = self.extract_items_from_venue(venue_details, market)
                self.items.extend(venue_items)

        logger.info(f"Scraping completed. Total markets: {len(self.markets)}, Total items: {len(self.items)}")

    def save_to_csv(self):
        """Save scraped data to CSV files"""
        logger.info("Saving data to CSV files...")

        # Save markets
        if self.markets:
            markets_file = os.path.join(self.output_dir, f'markets_{self.target_city}.csv')
            with open(markets_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.markets[0].keys())
                writer.writeheader()
                writer.writerows(self.markets)
            logger.info(f"Saved {len(self.markets)} markets to {markets_file}")

        # Save items
        if self.items:
            items_file = os.path.join(self.output_dir, f'items_{self.target_city}.csv')
            with open(items_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.items[0].keys())
                writer.writeheader()
                writer.writerows(self.items)
            logger.info(f"Saved {len(self.items)} items to {items_file}")
        else:
            logger.warning("No items found to save")

        # Save summary
        summary_file = os.path.join(self.output_dir, f'scrape_summary_{self.target_city}.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Wolt Markets Scraping Summary - {self.target_city.capitalize()}\n")
            f.write(f"{'='*50}\n")
            f.write(f"Scraped at: {datetime.now().isoformat()}\n")
            f.write(f"Target city: {self.target_city}\n")
            f.write(f"Total markets scraped: {len(self.markets)}\n")
            f.write(f"Total items scraped: {len(self.items)}\n")
            f.write(f"\nData saved to:\n")
            f.write(f"  - {os.path.join(self.output_dir, f'markets_{self.target_city}.csv')}\n")
            f.write(f"  - {os.path.join(self.output_dir, f'items_{self.target_city}.csv')}\n")

        logger.info(f"Summary saved to {summary_file}")

    def run(self):
        """Run the complete scraping process"""
        try:
            self.scrape_markets()
            self.save_to_csv()
            logger.info("Scraping process completed successfully!")
        except Exception as e:
            logger.error(f"Scraping failed with error: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    import sys

    target_city = "baku"
    if len(sys.argv) > 1:
        target_city = sys.argv[1]

    scraper = WoltMarketsScraper(output_dir="data", target_city=target_city)
    scraper.run()


if __name__ == "__main__":
    main()

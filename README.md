# Wolt Markets Scraper

A comprehensive Python scraper for collecting supermarket, item, and pricing data from Wolt's delivery platform.

## Features

- Scrapes all available cities and markets from Wolt
- Extracts detailed information about supermarkets and stores
- Collects comprehensive item data including:
  - Product names and descriptions
  - Current prices and original prices (for discounted items)
  - Discount amounts and percentages
  - Unit information and unit prices
  - Barcodes (GTIN)
  - Stock availability
  - Nutritional information (alcohol content, caffeine)
  - Dietary preferences and tags
  - Images and product metadata
- Exports all data to CSV format for easy analysis
- Implements rate limiting and error handling
- Detailed logging for monitoring scraping progress

## Data Points Captured

### Markets Data (markets.csv)
- Venue ID, name, and slug
- Full address and location coordinates
- City and country information
- Rating score and volume
- Price range
- Online status and delivery availability
- Delivery pricing and estimated times
- Store descriptions and tags

### Items Data (items.csv)
- Item ID and venue association
- Product name and description
- Current price and original price
- Discount information (amount and percentage)
- Unit information and unit pricing
- Barcode (GTIN)
- Image URLs
- Stock levels and purchase limits
- VAT percentage
- Dietary preferences and allergens
- Availability status
- Category and section information

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:

```bash
python scripts/markets.py
```

Or make it executable and run directly:

```bash
chmod +x scripts/markets.py
./scripts/markets.py
```

## Output

The scraper will create the following files in the `data/` directory:

- `markets.csv` - All supermarket/store information
- `items.csv` - All product/item information
- `scrape_summary.txt` - Summary of the scraping session

## API Endpoints Used

The scraper uses the following Wolt API endpoints:

1. **Cities API**: `https://restaurant-api.wolt.com/v1/cities`
   - Fetches all available cities

2. **Retail Markets API**: `https://consumer-api.wolt.com/v1/pages/retail?lat={lat}&lon={lon}`
   - Fetches all retail stores for a specific location

3. **Venue Details API**: `https://consumer-api.wolt.com/consumer-api/venue-content-api/v3/web/venue-content/slug/{slug}`
   - Fetches detailed information and full product catalog for a specific store

## Rate Limiting

The scraper includes a 0.5-second delay between requests to avoid overwhelming the API servers.

## Error Handling

- All HTTP requests include error handling
- Failed requests are logged but don't stop the scraping process
- JSON parsing errors are caught and logged

## Logging

The scraper provides detailed logging output showing:
- Progress through cities and markets
- Number of items extracted from each venue
- Any errors encountered during scraping
- Final summary of scraped data

## Notes

- The scraper processes all cities available in Wolt's API
- For each city, it fetches all retail markets (supermarkets, pharmacies, etc.)
- For each market, it extracts the complete product catalog
- All data is saved with timestamps for tracking when it was scraped
- No data points are lost - the scraper captures all available information from the API

## Data Privacy

This scraper only accesses publicly available data from Wolt's API. It does not require authentication or access to private user data.

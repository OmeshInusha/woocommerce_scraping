# woocommerce_scraping
Scrape every woocommerce website with just 6 parameters.

# Product Scraper

A comprehensive web scraping tool designed to extract product information from e-commerce websites using sitemaps, categorize products using AI, and store the data in a MySQL database.

## Features

- Extracts product data from e-commerce sites using sitemaps
- Categorizes products automatically using Llama 3.1 AI model via OpenRouter API
- Identifies product brands from titles
- Stores structured product data in MySQL database
- Handles duplicate entries with update capabilities
- Scheduled periodic scraping with configurable intervals

## Requirements

- Python 3.6+
- MySQL Server
- Internet connection for API requests

## Dependencies

```
requests
beautifulsoup4
mysql-connector-python
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/OmeshInusha/woocommerce_scraping.git
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your MySQL database using the schema provided in `schema.sql`

4. Configure your API keys and database connection in the script or through environment variables

## Configuration

Before running the script, you need to configure:

1. OpenRouter API key (`OPENROUTER_API_KEY`)
2. Your site URL (`YOUR_SITE_URL`)
3. Application name (`YOUR_APP_NAME`)
4. MySQL database connection parameters:
   - Host
   - Username
   - Password
   - Database name

### MYSQL TABLE EXAMPLE SCHEME

```
CREATE TABLE CALLED 'Products'

| id  | title   | description  | price  | store  | link  | image_link  | category  | brand  | out_of_stock | listing_date | verified_date | end_date | compare_data |


```
### HOW TO FIND JSON+LD OF A SITE 

Go to one of your target website  product page
press ``` ctrl + U ``` and find for 

```

		<script type="application/ld+json">{"@context":"https:\/\/schema.org\/","@graph":[{"@context":"https:\/\/schema.org\/","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"item":{"name":"Home","@id":"https:\/\/xmobile.lk"}},{"@type":"ListItem","position":2,"item":{"name":"Mobile Phones","@id":"https:\/\/xmobile.lk\/product-category\/mobile-phones\/"}},{"@type":"ListItem","position":3,"item":{"name":"Xiaomi","@id":"https:\/\/xmobile.lk\/product-category\/mobile-phones\/xiaomi\/"}},{"@type":"ListItem","position":4,"item":{"name":"Xiaomi Redmi Note 14 Pro Plus 5G 12GB RAM 512GB","@id":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/"}}]},{"@context":"https:\/\/schema.org\/","@graph":[{"@type":"Product","@id":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/#product","name":"Xiaomi Redmi Note 14 Pro Plus 5G 12GB RAM 512GB","url":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/","description":"Display:\u00a06.67\u2033 OLED, 120Hz refresh rate.\r\n \tProcessor:\u00a0Dimensity 7025 Ultra, 5G-ready.\r\n \tCameras:\u00a050MP + 2MP rear, 16MP front.\r\n \tBattery:\u00a05110mAh, 45W fast charging.\r\n \tDesign:\u00a0Lightweight, Gorilla Glass 5.\r\n \tValue:\u00a0Budget-friendly with premium features.\r\n \tWarranty:\u00a0One Year Warranty","image":"https:\/\/xmobile.lk\/wp-content\/uploads\/2025\/03\/Xiaomi-Redmi-Note-14-Pro-5G-8GB-RAM-256GB3.jpg","sku":"Xiaomi Redmi Note 14 Pro Plus 5G 12GB RAM 512GB","offers":[{"@type":"Offer","priceSpecification":[{"@type":"UnitPriceSpecification","price":"149999.00","priceCurrency":"LKR","valueAddedTaxIncluded":false,"validThrough":"2026-12-31"}],"priceValidUntil":"2026-12-31","availability":"http:\/\/schema.org\/InStock","url":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/","seller":{"@type":"Organization","name":"XMobile","url":"https:\/\/xmobile.lk"}}],"brand":{"@type":"Brand","name":"Xiaomi"}},{"@type":"Product","@id":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/#product","name":"Xiaomi Redmi Note 14 Pro Plus 5G 12GB RAM 512GB","url":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/","description":"Display:\u00a06.67\u2033 OLED, 120Hz refresh rate.\r\n \tProcessor:\u00a0Dimensity 7025 Ultra, 5G-ready.\r\n \tCameras:\u00a050MP + 2MP rear, 16MP front.\r\n \tBattery:\u00a05110mAh, 45W fast charging.\r\n \tDesign:\u00a0Lightweight, Gorilla Glass 5.\r\n \tValue:\u00a0Budget-friendly with premium features.\r\n \tWarranty:\u00a0One Year Warranty","image":"https:\/\/xmobile.lk\/wp-content\/uploads\/2025\/03\/Xiaomi-Redmi-Note-14-Pro-5G-8GB-RAM-256GB3.jpg","sku":"Xiaomi Redmi Note 14 Pro Plus 5G 12GB RAM 512GB","offers":[{"@type":"Offer","priceSpecification":[{"@type":"UnitPriceSpecification","price":"149999.00","priceCurrency":"LKR","valueAddedTaxIncluded":false,"validThrough":"2026-12-31"}],"priceValidUntil":"2026-12-31","availability":"http:\/\/schema.org\/InStock","url":"https:\/\/xmobile.lk\/product\/xiaomi-redmi-note-14-pro-plus-5g-12gb-ram-512gb\/","seller":{"@type":"Organization","name":"XMobile","url":"https:\/\/xmobile.lk"}}],"brand":{"@type":"Brand","name":"Xiaomi"}}]}]}</script>

```
and from this find path for next mention parameters

## Usage

Run the script from the command line:

```
python wsm.py
```

You will be prompted to enter the following information:

1. `sitemap` - URL of the website's sitemap
2. `Store name` - Name of the e-commerce store
3. `title` - JSON field name for product title
4. `description` - JSON field name for product description
5. `price sc` - JSON field name for product price
6. `image sc` - JSON field name for product image URL
7. `av` - JSON field name for product availability
8. `seller` - JSON field name for seller information
9. `char` - Character set for price processing
10. `day` - Scraping interval in days

## How It Works

1. The script fetches all product URLs from the provided sitemap
2. For each product URL:
   - It extracts product data from the webpage (using structured JSON-LD data where available)
   - Sends the product title to the AI model for categorization
   - Processes and cleans the extracted data
   - Stores the data in the MySQL database
3. The script runs continuously, repeating the process at the specified interval

## AI Categorization

The script uses a Llama 3.1 model to categorize products into a hierarchical structure:
- Main category
- Sub-category 1
- Sub-category 2

It also extracts the brand name from the product title.

## Database Schema

The script stores product data in a `products` table with the following structure:

- `title` - Product title
- `description` - Product description
- `price` - Product price
- `store` - Store name
- `link` - Product URL (primary key)
- `image_link` - Product image URL
- `category` - Product category (formatted as "main,sub1,sub2")
- `brand` - Product brand
- `out_of_stock` - Stock status
- `listing_date` - Initial listing date
- `verified_date` - Last verification date
- `end_date` - End date for the listing
- `compare_data` - Additional comparison data

## Customization

You can modify the `system_prompt` variable to adjust how the AI categorizes products.

## Error Handling

The script includes error handling for:
- Network request failures
- JSON parsing errors
- Database connection issues
- Invalid product data

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Disclaimer

This tool is intended for legitimate data collection purposes only. Always respect website terms of service and robots.txt directives when scraping. Ensure you have permission to scrape the targeted websites.

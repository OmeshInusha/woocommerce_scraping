import requests
import json
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
import site_value_m
import traceback
import logging
from datetime import datetime
import time
import re

system_prompt = '''you are an AI model tasked with categorizing products and extracting their brands based on product titles. Given a product title, you should output the main category, sub-category 1, and sub-category 2 in the following hierarchical format: main_category > sub_category_1 > sub_category_2. Additionally, extract the brand of the product.

Instructions:
Categorization:

Main Category: Identify the primary category of the product (e.g., Electronics, Clothing, Home & Kitchen).
Sub-Category 1: Identify the first sub-category within the main category.
Sub-Category 2: Identify the second sub-category within the first sub-category.
Brand Extraction:

Extract the brand from the product title. The brand is typically the first identifiable word or phrase that represents a known brand.
Output Format:

Structure the output in JSON format with the following fields:
main_category: The primary category of the product.
sub_category_1: The first sub-category within the main category.
sub_category_2: The second sub-category within the first sub-category.
brand: The brand of the product.
Examples:
Example 1:
Input: "Samsung Galaxy S21 Ultra 5G Smartphone"
Output:
{
  "main_category": "Electronics",
  "sub_category_1": "Mobile Phones",
  "sub_category_2": "Smartphones",
  "brand": "Samsung"
}
Example 2:
Input: "Nike Air Max 270 Running Shoes"
Output:
{
  "main_category": "Clothing",
  "sub_category_1": "Footwear",
  "sub_category_2": "Running Shoes",
  "brand": "Nike"
}
Example 3:
Input: "Apple MacBook Pro 16-inch Laptop"
Output:
{
  "main_category": "Electronics",
  "sub_category_1": "Computers",
  "sub_category_2": "Laptops",
  "brand": "Apple"
}
Edge Cases and Error Handling:
If a title contains multiple potential brands, choose the most prominent one based on common usage.
If a category or sub-category is unclear, use "Unknown" as a placeholder.
Ensure the JSON output is correctly formatted even if certain fields cannot be confidently identified. 
THINGS NOT TO INSERT - 
*NO OTHER WORDS JUST JSON FORMAT
*PROGRAMMING CODES
'''

OPENROUTER_API_KEY = 'your_open_router_api_key'
YOUR_SITE_URL = 'your_site'
YOUR_APP_NAME = 'your app name'  # use env

db = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=20,  # Set the pool size to 20 according to your expected load
    host="ipaddress", # change to localhost when push to production
    user="admin",
    password="admin",
    database="admin"
)
def load_user_agents(file_path):
    with open(file_path, 'r') as file:
        user_agents = [line.strip() for line in file if line.strip()]
    return user_agents
def send_message(prompt, system_prompt):
    max_tokens = 250
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": f"{YOUR_SITE_URL}",
            "X-Title": f"{YOUR_APP_NAME}",
        },
        data=json.dumps({
            "model": "meta-llama/llama-3.1-8b-instruct", # use a cheap model
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "system", "content": system_prompt}
            ],
            "max_tokens": max_tokens
        })
    )

    if response.status_code == 200:
        try:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        except Exception as e:
            tb = traceback.format_exc()
            error_message = f"An error occurred: {e}\nTraceback details:\n{tb}"
            site_value_m.send_telegram_message(error_message)
            return 'none'
    else:
        print(f"Error: {response.status_code}")
        site_value_m.send_telegram_message(response.status_code)
        return f"Error: {response.status_code}"


def product_data_conv(links, store, char, cursor, connection, cursor_1 , name , description , price_sc , image_sc , av ,seller):
    # Define your JSON schema field mapping here
    SCHEMA_MAP = {
        'title': name,  # Map 'name' in code to 'title' in user schema
        'description': description,
        'price_field': price_sc,
        'image_field': image_sc,
        'availability_field': av,
        'stock_indicator': seller  # Stock status indicator
    }

    data = []
    today_date = datetime.today()
    end_date = datetime.strptime('2025-09-29', '%Y-%m-%d')

    for link in links:
        time.sleep(0)
        try:
            product_data = extract_product_data(link)
            print(f"Extracted product data: {product_data}")

            if isinstance(product_data, list):
                for product in product_data:
                    if not isinstance(product, dict):
                        print(f"Invalid product format in list: {type(product)}")
                        continue

                    # Check if link exists using schema-mapped fields
                    cursor_1.execute("SELECT COUNT(*) FROM products WHERE link = %s", (link,))
                    if cursor_1.fetchone()[0] > 0:
                        print(f"Link exists: {link}, skipping.")
                        already = True
                    else:
                        already = False

                    # Extract data using schema mapping
                    title = product.get(SCHEMA_MAP['title'], '').strip()
                    body_html = product.get(SCHEMA_MAP['description'], '')
                    raw_price = product.get(SCHEMA_MAP['price_field'], '')
                    image_src = product.get(SCHEMA_MAP['image_field'], '')
                    stock_status = product.get(SCHEMA_MAP['availability_field'], '')
                    if 'OutOfStock' in stock_status:
                        print('Out of stock product')
                        continue
                    # Price processing
                    try:
                        price = int(raw_price)
                    except:
                        # Fallback to direct scraping if price conversion fails
                        response = requests.get(link)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, "html.parser")
                        soup = soup.find("p", {"class": "price"})
                        price_element = soup.find("span", {"class": "woocommerce-Price-amount amount"})
                        print(price_element)
                        price = site_value_m.price_sort(price_element.get_text().strip(),
                                                        char) if price_element else None
                        if not price:
                            print("Price not found.")
                            continue

                    # Description processing
                    soup = BeautifulSoup(body_html.encode("utf-8"), 'html.parser')
                    body_html = soup.get_text()
                    body_html = re.sub(r'[^\x00-\x7F]+', '', body_html)

                    # Stock status determination
                    out_of_stock = "FALSE"

                    # Rest of the processing remains unchanged
                    print(
                        f"Title: {title}, Description: {body_html}, Price: {price}, Image: {image_src}, Stock: {out_of_stock}")

                    if already:
                        category = 'other'
                        brand = 'other'
                    else:
                        # Category and brand processing
                        output = send_message(title, system_prompt)

                        if not output or output.lower() == 'none':
                            print("Skipping due to empty output")
                            continue

                        if 'json' in output:
                            output = output.replace('json', '')

                        try:
                            pr_data = json.loads(output)
                            main_category = pr_data.get('main_category', 'Unknown')
                            sub_category_1 = pr_data.get('sub_category_1', 'Unknown')
                            sub_category_2 = pr_data.get('sub_category_2', 'Unknown')
                            category = f'{main_category},{sub_category_1},{sub_category_2}'
                            print(category)
                            brand = pr_data.get('brand', 'Unknown')
                        except json.JSONDecodeError:
                            print("Failed to parse category data")
                            continue

                    # Prepare and insert data
                    product_tuple = (
                        title, body_html, price, store, link, image_src,
                        category, brand, out_of_stock, today_date.strftime('%Y-%m-%d'),
                        today_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), None
                    )
                    data.append(product_tuple)
                    insert_data(cursor, data, connection)
                    connection.commit()
            else:
                print(f"Invalid product_data format: {type(product_data)}")
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            continue

    connection.close()
    print('Data added successfully')

def fetch_sitemap_links(sitemap_url):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(sitemap_url)
    response.raise_for_status()  # Ensure we handle bad responses
    soup = BeautifulSoup(response.content, 'xml')

    # Extracting the links
    links = [loc.text for loc in soup.find_all('loc')]

    # Filter out image links (assuming image links contain '.jpg', '.png', or '.webp')
    product_links = [link for link in links if not any(ext in link.lower() for ext in ['.jpg', '.png', '.webp', '.jpeg'])]

    print(product_links)
    return product_links




def insert_data(cursor, data ,connection):
    try:
        cursor.execute("USE main_scrape")
        query = """
        INSERT INTO products (title, description, price, store, link, image_link, category, brand, out_of_stock, listing_date, verified_date, end_date, compare_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            description = VALUES(description),
            price = VALUES(price),
            image_link = VALUES(image_link),
            out_of_stock = VALUES(out_of_stock),
            listing_date = VALUES(listing_date),
            verified_date = VALUES(verified_date),
            end_date = VALUES(end_date)
        """
        cursor.executemany(query, data)
        connection.commit()
        print("Data inserted successfully - function.")
    except Error as e:
        connection.rollback()
        logging.error(f"Error while inserting data: {e}")
def main(sitemap,store_name,char,name , description , price_sc , image_sc , av ,seller):
    all_links = fetch_sitemap_links(sitemap)
    print(len(all_links))
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor_1 = connection.cursor()
    product_data_conv(all_links,store_name,char,cursor,connection,cursor_1,name , description , price_sc , image_sc , av ,seller)
def extract_product_data(url):
    # Define headers to mimic a real browser
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }

    # Use a session to maintain cookies and headers
    session = requests.Session()
    session.headers.update(headers)

    try:
        # Send a GET request to the URL
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <script> tags with type "application/ld+json"
    scripts = soup.find_all('script', type='application/ld+json')

    product_data = []
    for i, script in enumerate(scripts):
        try:
            # Load JSON content from the <script> tag
            data = json.loads(script.string)

            # Handle cases with '@graph'
            if isinstance(data, dict) and '@graph' in data:
                for item in data['@graph']:
                    if item.get('@type') == 'Product':
                        product_data.append(parse_product(item))

            # Handle cases without '@graph'
            elif isinstance(data, dict) and data.get('@type') == 'Product':
                product_data.append(parse_product(data))

        except json.JSONDecodeError as e:
            print(f"Invalid JSON in script #{i}: {e}")
            print(url)
        except Exception as e:
            print(f"Error processing script #{i}: {e}")

    if not product_data:
        print(url)
        print("No valid product data found.")
    return product_data


def parse_product(item):
    """Extract product details safely with default values."""
    try:
        offers = item.get('offers', [{}])[0] if isinstance(item.get('offers'), list) else item.get('offers', {})
        return {
            'name': item.get('name', 'N/A'),
            'url': item.get('url', 'N/A'),
            'description': item.get('description', 'N/A'),
            'image': item.get('image', 'N/A'),
            'sku': item.get('sku', 'N/A'),
            'price': offers.get('price', 'N/A'),
            'priceCurrency': offers.get('priceCurrency', 'N/A'),
            'availability': offers.get('availability', 'N/A'),
            'seller': offers.get('seller', {}).get('name', 'N/A'),
        }
    except Exception as e:
        print(f"Error parsing product: {e}")
        return {}



if __name__ == "__main__":
    sitemap = input('sitemap - ')
    store_name = input('Store name - ')
    name = input('title - ')
    description = input('description - ')
    price_sc = input('price sc- ')
    image_sc = input('image sc - ')
    av = input('av - ')
    seller = input('seller - ')
    char = input('char - ')
    days = input('day - ')
    seconds = int(days) * 24 * 60 * 60

    while True:
        main(sitemap,store_name,char,name , description , price_sc , image_sc , av ,seller)
        time.sleep(int(seconds))






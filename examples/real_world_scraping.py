#!/usr/bin/env python3
"""
Real-world scraping example with requests

This example shows how to scrape actual Next.js websites.
Note: Always respect robots.txt and rate limits when scraping.
"""

import requests
import time
from nextjs_hydration_parser import NextJSHydrationDataExtractor


def scrape_with_requests(url, delay=1):
    """
    Scrape a URL and extract Next.js hydration data

    Args:
        url (str): URL to scrape
        delay (int): Delay in seconds between requests (be respectful!)

    Returns:
        dict: Extracted data
    """

    # Headers to appear more like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.text)} characters")

        # Add delay to be respectful
        time.sleep(delay)

        return response.text

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_and_analyze(html_content, url):
    """Extract and analyze hydration data from HTML"""

    if not html_content:
        return

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print(f"\n=== Analysis for {url} ===")
    print(f"Found {len(chunks)} hydration chunks")

    if not chunks:
        print("No Next.js hydration data found - this might not be a Next.js site")
        return

    # Basic statistics
    total_items = sum(len(chunk["extracted_data"]) for chunk in chunks)
    error_chunks = len([c for c in chunks if c["chunk_id"] == "error"])

    print(f"Total data items: {total_items}")
    print(f"Error chunks: {error_chunks}")

    # Analyze data types
    data_types = {}
    for chunk in chunks:
        for item in chunk["extracted_data"]:
            item_type = item["type"]
            data_types[item_type] = data_types.get(item_type, 0) + 1

    print(f"Data types found: {dict(data_types)}")

    # Get all keys
    all_keys = extractor.get_all_keys(chunks, max_depth=2)
    if all_keys:
        print(f"Most common keys: {dict(list(all_keys.items())[:10])}")

    # Look for common e-commerce patterns
    ecommerce_patterns = ["product", "price", "cart", "category", "inventory"]
    found_patterns = []

    for pattern in ecommerce_patterns:
        matches = extractor.find_data_by_pattern(chunks, pattern)
        if matches:
            found_patterns.append(f"{pattern}({len(matches)})")

    if found_patterns:
        print(f"E-commerce patterns found: {', '.join(found_patterns)}")

    # Show sample data
    print("\n--- Sample Data ---")
    sample_count = 0
    for chunk in chunks[:3]:  # Show first 3 chunks
        if chunk["chunk_id"] != "error" and sample_count < 2:
            for item in chunk["extracted_data"][:1]:  # Show first item
                data_preview = str(item["data"])[:200]
                print(f"Chunk {chunk['chunk_id']} ({item['type']}): {data_preview}...")
                sample_count += 1


def test_known_nextjs_sites():
    """Test with some known Next.js sites (educational purposes)"""

    # Note: These are examples - always check robots.txt and terms of service
    test_sites = [
        "https://nextjs.org",  # Official Next.js site
        "https://vercel.com",  # Vercel (makers of Next.js)
    ]

    print("Testing known Next.js sites...")
    print("Note: This is for educational purposes only.")
    print("Always respect robots.txt and site terms of service.\n")

    for url in test_sites:
        html_content = scrape_with_requests(url, delay=2)  # Be respectful with delays
        extract_and_analyze(html_content, url)
        print("-" * 50)


def scrape_local_file(file_path):
    """Scrape from a local HTML file"""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        print(f"Reading local file: {file_path}")
        extract_and_analyze(html_content, file_path)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")


def main():
    """Main function with examples"""

    print("Real-world Next.js Scraping Examples")
    print("=" * 40)

    # Example 1: Test with known Next.js sites
    response = input("Test with known Next.js sites? (y/n): ").lower().strip()
    if response == "y":
        test_known_nextjs_sites()

    # Example 2: Custom URL
    custom_url = input(
        "\nEnter a custom URL to test (or press Enter to skip): "
    ).strip()
    if custom_url:
        html_content = scrape_with_requests(custom_url)
        extract_and_analyze(html_content, custom_url)

    # Example 3: Local file
    file_path = input(
        "\nEnter path to local HTML file (or press Enter to skip): "
    ).strip()
    if file_path:
        scrape_local_file(file_path)

    print("\nRemember to:")
    print("- Always respect robots.txt")
    print("- Add appropriate delays between requests")
    print("- Check website terms of service")
    print("- Consider rate limiting for production use")


if __name__ == "__main__":
    main()

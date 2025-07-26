#!/usr/bin/env python3
"""
Sample HTML file parsing example

This example demonstrates parsing the included sample Next.js HTML file
that contains realistic e-commerce hydration data.
"""

import json
import os
from pathlib import Path
from nextjs_hydration_parser import NextJSHydrationDataExtractor


def load_sample_html():
    """Load the sample HTML file"""

    # Get the path to the sample HTML file
    current_dir = Path(__file__).parent
    sample_file = current_dir / "sample_nextjs_page.html"

    if not sample_file.exists():
        print(f"ERROR: Sample file not found: {sample_file}")
        return None

    with open(sample_file, "r", encoding="utf-8") as f:
        return f.read()


def analyze_sample_data(chunks):
    """Analyze the extracted data from sample HTML"""

    print("=== SAMPLE DATA ANALYSIS ===")
    print(f"Total chunks found: {len(chunks)}")

    # Overview of chunk IDs
    chunk_ids = [chunk["chunk_id"] for chunk in chunks if chunk["chunk_id"] != "error"]
    print(f"Chunk IDs: {sorted(set(chunk_ids))}")

    # Multi-chunk analysis
    multi_chunks = [chunk for chunk in chunks if chunk["chunk_count"] > 1]
    if multi_chunks:
        print(f"Multi-chunk data found: {len(multi_chunks)} chunks")
        for chunk in multi_chunks:
            print(f"  Chunk {chunk['chunk_id']}: {chunk['chunk_count']} parts")

    # Data type analysis
    data_types = {}
    for chunk in chunks:
        for item in chunk["extracted_data"]:
            data_type = item["type"]
            data_types[data_type] = data_types.get(data_type, 0) + 1

    print(f"Data types found: {dict(data_types)}")


def extract_ecommerce_data(chunks, extractor):
    """Extract specific e-commerce data patterns"""

    print("\n=== E-COMMERCE DATA EXTRACTION ===")

    # Extract products
    products = extractor.find_data_by_pattern(chunks, "product")
    print(f"Products found: {len(products)} matches")

    if products:
        for i, product_match in enumerate(products[:3]):  # Show first 3
            product_data = product_match["value"]
            if isinstance(product_data, list) and len(product_data) > 0:
                product = product_data[0]  # First product in array
                print(
                    f"  Product {i+1}: {product.get('name', 'Unknown')} - ${product.get('price', 'N/A')}"
                )
            elif isinstance(product_data, dict):
                print(
                    f"  Product {i+1}: {product_data.get('name', 'Unknown')} - ${product_data.get('price', 'N/A')}"
                )

    # Extract categories
    categories = extractor.find_data_by_pattern(chunks, "categor")
    print(f"Categories found: {len(categories)} matches")

    # Extract user/cart data
    cart_data = extractor.find_data_by_pattern(chunks, "cart")
    print(f"Cart data found: {len(cart_data)} matches")

    if cart_data:
        for cart_match in cart_data[:1]:  # Show first match
            cart = cart_match["value"]
            if isinstance(cart, dict):
                items = cart.get("items", [])
                total = cart.get("total", 0)
                print(f"  Cart: {len(items)} items, total: ${total}")

    # Extract recommendations
    recommendations = extractor.find_data_by_pattern(chunks, "recommend")
    print(f"Recommendations found: {len(recommendations)} matches")


def extract_api_data(chunks):
    """Extract API response data"""

    print("\n=== API DATA EXTRACTION ===")

    api_chunks = []
    for chunk in chunks:
        for item in chunk["extracted_data"]:
            if item["type"] == "colon_separated":
                identifier = item.get("identifier", "").lower()
                if "api" in identifier or "config" in identifier:
                    api_chunks.append(
                        {
                            "identifier": item.get("identifier", "unknown"),
                            "data": item["data"],
                        }
                    )

    print(f"API/Config data chunks: {len(api_chunks)}")

    for api_chunk in api_chunks:
        identifier = api_chunk["identifier"]
        data = api_chunk["data"]
        print(f"  {identifier}: {type(data).__name__}")

        if isinstance(data, dict):
            keys = list(data.keys())[:5]  # First 5 keys
            print(f"    Keys: {keys}")


def show_key_analysis(chunks, extractor):
    """Show key analysis of all data"""

    print("\n=== KEY ANALYSIS ===")

    # Get all keys
    all_keys = extractor.get_all_keys(chunks, max_depth=3)

    # Sort by frequency
    sorted_keys = sorted(all_keys.items(), key=lambda x: x[1], reverse=True)

    print(f"Total unique keys found: {len(all_keys)}")
    print("Most common keys:")

    for key, count in sorted_keys[:15]:  # Top 15 keys
        print(f"  {key}: {count} occurrences")


def demonstrate_search_patterns(chunks, extractor):
    """Demonstrate various search patterns"""

    print("\n=== SEARCH PATTERN DEMONSTRATIONS ===")

    # Common e-commerce search patterns
    patterns = [
        ("price", "Price-related data"),
        ("stock", "Inventory/stock data"),
        ("brand", "Brand information"),
        ("rating", "Ratings and reviews"),
        ("user", "User-related data"),
        ("analytics", "Analytics and tracking"),
        ("config", "Configuration data"),
        ("error", "Error handling"),
    ]

    for pattern, description in patterns:
        matches = extractor.find_data_by_pattern(chunks, pattern)
        if matches:
            print(f"  {description}: {len(matches)} matches")

            # Show sample data for first match
            sample = matches[0]["value"]
            if isinstance(sample, (dict, list)):
                sample_str = (
                    json.dumps(sample, indent=2)[:200] + "..."
                    if len(str(sample)) > 200
                    else json.dumps(sample, indent=2)
                )
                print(f"    Sample: {sample_str}")
            else:
                print(f"    Sample: {str(sample)[:100]}...")


def main():
    """Main demonstration function"""

    print("Next.js Hydration Parser - Sample HTML Analysis")
    print("=" * 60)

    # Load sample HTML
    html_content = load_sample_html()
    if not html_content:
        return

    print(f"Loaded sample HTML: {len(html_content)} characters")

    # Parse hydration data
    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    # Run analysis
    analyze_sample_data(chunks)
    extract_ecommerce_data(chunks, extractor)
    extract_api_data(chunks)
    show_key_analysis(chunks, extractor)
    demonstrate_search_patterns(chunks, extractor)

    # Show raw data for one chunk
    print("\n=== SAMPLE RAW DATA ===")
    if chunks and len(chunks[0]["extracted_data"]) > 0:
        sample_item = chunks[0]["extracted_data"][0]
        print(f"Chunk ID: {chunks[0]['chunk_id']}")
        print(f"Data type: {sample_item['type']}")

        if isinstance(sample_item["data"], dict):
            print("Sample data structure:")
            print(json.dumps(sample_item["data"], indent=2)[:500] + "...")
        else:
            print(f"Raw data: {str(sample_item['data'])[:300]}...")

    print("\n" + "=" * 60)
    print("Analysis complete! This demonstrates parsing a realistic Next.js page")
    print("with complex e-commerce data including products, categories, user data,")
    print("shopping cart, recommendations, analytics, and more.")


if __name__ == "__main__":
    main()

# Next.js Hydration Parser

[![PyPI version](https://badge.fury.io/py/nextjs-hydration-parser.svg)](https://badge.fury.io/py/nextjs-hydration-parser)
[![Python versions](https://img.shields.io/pypi/pyversions/nextjs-hydration-parser.svg)](https://pypi.org/project/nextjs-hydration-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized Python library for extracting and parsing Next.js 13+ hydration data from raw HTML pages. When scraping Next.js applications, the server-side rendered HTML contains complex hydration data chunks embedded in `self.__next_f.push()` calls that need to be properly assembled and parsed to access the underlying application data.

## The Problem

Next.js 13+ applications with App Router use a sophisticated hydration system that splits data across multiple script chunks in the raw HTML. When you scrape these pages (before JavaScript execution), you get fragments like:

```html
<script>self.__next_f.push([1,"partial data chunk 1"])</script>
<script>self.__next_f.push([1,"continuation of data"])</script>
<script>self.__next_f.push([2,"{\"products\":[{\"id\":1,\"name\":\"Product\"}]}"])</script>
```

This data is:
- **Split across multiple chunks** that need to be reassembled
- **Encoded in various formats** (JSON strings, base64, escaped content)
- **Mixed with rendering metadata** that needs to be filtered out
- **Difficult to parse** due to complex escaping and nested structures

This library solves these challenges by intelligently combining chunks, handling multiple encoding formats, and extracting the meaningful application data.

## Features

- �️ **Web Scraping Focused** - Designed specifically for parsing raw Next.js 13+ pages before JavaScript execution
- 🧩 **Chunk Reassembly** - Intelligently combines data fragments split across multiple `self.__next_f.push()` calls
- 🔍 **Multi-format Parsing** - Handles JSON strings, base64-encoded data, escaped content, and complex nested structures
- 🎯 **Data Extraction** - Filters out rendering metadata to extract meaningful application data (products, users, API responses, etc.)
- 🛠️ **Robust Error Handling** - Continues processing even with malformed chunks, providing debugging information
- 🔎 **Pattern Matching** - Search and filter extracted data by keys or content patterns
- ⚡ **Performance Optimized** - Efficiently processes large HTML files with hundreds of hydration chunks

## Use Cases

Perfect for:
- **E-commerce scraping** - Extract product catalogs, prices, and inventory data
- **Content aggregation** - Collect articles, blog posts, and structured content
- **API reverse engineering** - Understand data structures used by Next.js applications
- **SEO analysis** - Extract meta information and structured data for analysis

## Installation

```bash
pip install nextjs-hydration-parser
```

### Requirements

- Python 3.7+
- `chompjs` for JavaScript object parsing
- `requests` (for scraping examples)

The library is lightweight with minimal dependencies, designed for integration into existing scraping pipelines.

## Quick Start

```python
from nextjs_hydration_parser import NextJSHydrationDataExtractor
import requests

# Create an extractor instance
extractor = NextJSHydrationDataExtractor()

# Scrape a Next.js page (before JavaScript execution)
response = requests.get('https://example-nextjs-ecommerce.com/products')
html_content = response.text

# Extract and parse the hydration data
chunks = extractor.parse(html_content)

# Process the results to find meaningful data
for chunk in chunks:
    print(f"Chunk ID: {chunk['chunk_id']}")
    for item in chunk['extracted_data']:
        if item['type'] == 'colon_separated':
            # Often contains API response data
            print(f"API Data: {item['data']}")
        elif 'products' in str(item['data']):
            # Found product data
            print(f"Products: {item['data']}")
```

### Real-world Example: E-commerce Scraping

```python
# Extract product data from a Next.js e-commerce site
extractor = NextJSHydrationDataExtractor()
html_content = open('product_page.html', 'r').read()

chunks = extractor.parse(html_content)

# Find product information
products = extractor.find_data_by_pattern(chunks, 'product')
for product_data in products:
    if isinstance(product_data['value'], dict):
        product = product_data['value']
        print(f"Product: {product.get('name', 'Unknown')}")
        print(f"Price: ${product.get('price', 'N/A')}")
        print(f"Stock: {product.get('inventory', 'Unknown')}")
```

## ⚡ Lightweight Mode (Fast Parsing)

For large pages with hundreds of chunks, use **lightweight mode** when you know what data you're looking for. This can be **10-15x faster** than full parsing!

### When to Use Lightweight Mode

- Large HTML files (> 500KB)
- Pages with many hydration chunks
- You know the specific data keys you need (e.g., "products", "catalog", "items")
- Performance is critical

### Quick Example

```python
from nextjs_hydration_parser import NextJSHydrationDataExtractor

extractor = NextJSHydrationDataExtractor()
html_content = open('large_nextjs_page.html', 'r').read()

# Method 1: Full parsing (slow - 12+ seconds)
chunks = extractor.parse(html_content)
results = extractor.find_data_by_pattern(chunks, 'products')

# Method 2: Lightweight mode (fast - <1 second!) ⚡
results = extractor.parse_and_find(html_content, ['products'])

# Both methods return the same data, but lightweight is 14x faster!
print(f"Found {len(results)} matching items")
for result in results:
    print(f"Key: {result['key']}")
    print(f"Data: {result['value']}")
```

### Performance Comparison

```python
import time

# Full parsing
start = time.time()
full_chunks = extractor.parse(html_content)
full_results = extractor.find_data_by_pattern(full_chunks, 'product')
print(f"Full parsing: {time.time() - start:.2f}s")  # ~12.4s

# Lightweight mode
start = time.time()
light_results = extractor.parse_and_find(html_content, ['product'])
print(f"Lightweight: {time.time() - start:.2f}s")   # ~0.9s (14x faster!)
```

### Advanced Lightweight Usage

```python
# Search for multiple patterns at once
patterns = ['products', 'listings', 'inventory', 'prices']
results = extractor.parse_and_find(html_content, patterns)

# Or use manual lightweight parsing for more control
chunks = extractor.parse(
    html_content, 
    lightweight=True, 
    target_patterns=['listingsConnection', 'productData']
)

# Only chunks containing your patterns are fully parsed
for chunk in chunks:
    if not chunk.get('_skipped'):
        print(f"Chunk {chunk['chunk_id']} contains target data")
        # Process extracted_data as usual
```

### Real-world Example: E-commerce Category Scraping

```python
# Extract product listings from a large e-commerce category page
extractor = NextJSHydrationDataExtractor()

with open('ecommerce_category.html', 'r') as f:
    html = f.read()

# Fast extraction using lightweight mode
results = extractor.parse_and_find(html, ['products', 'catalog', 'items'])

for result in results:
    if result['key'] in ['products', 'catalog']:
        data = result['value']
        
        # Access product listings
        if isinstance(data, list):
            print(f"Found {len(data)} products")
            
            for product in data[:5]:  # Show first 5
                print(f"- {product.get('name', 'N/A')}: ${product.get('price', 'N/A')}")
```

## Advanced Usage

### Scraping Complex Next.js Applications

```python
import requests
from nextjs_hydration_parser import NextJSHydrationDataExtractor

def scrape_nextjs_data(url):
    """Scrape and extract data from a Next.js application"""
    
    # Get raw HTML (before JavaScript execution)
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; DataExtractor/1.0)'}
    response = requests.get(url, headers=headers)
    
    # Parse hydration data
    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(response.text)
    
    # Extract meaningful data
    extracted_data = {}
    
    for chunk in chunks:
        if chunk['chunk_id'] == 'error':
            continue  # Skip malformed chunks
            
        for item in chunk['extracted_data']:
            data = item['data']
            
            # Look for common data patterns
            if isinstance(data, dict):
                # API responses often contain these keys
                for key in ['products', 'users', 'posts', 'data', 'results']:
                    if key in data:
                        extracted_data[key] = data[key]
                        
    return extracted_data

# Usage
data = scrape_nextjs_data('https://nextjs-shop.example.com')
print(f"Found {len(data.get('products', []))} products")
```

### Handling Large HTML Files

When scraping large Next.js applications, use lightweight mode for better performance:

```python
# Read from file
with open('large_nextjs_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Use lightweight mode when you know what you're looking for (RECOMMENDED)
extractor = NextJSHydrationDataExtractor()
results = extractor.parse_and_find(html_content, ['products', 'listings'])

# Or full parse if you need everything
chunks = extractor.parse(html_content)
print(f"Found {len(chunks)} hydration chunks")

# Get overview of all available data keys
all_keys = extractor.get_all_keys(chunks)
print("Most common data keys:")
for key, count in list(all_keys.items())[:20]:
    print(f"  {key}: {count} occurrences")

# Focus on specific data types
api_data = []
for chunk in chunks:
    for item in chunk['extracted_data']:
        if item['type'] == 'colon_separated' and 'api' in item.get('identifier', '').lower():
            api_data.append(item['data'])

print(f"Found {len(api_data)} API data chunks")
```

## API Reference

### `NextJSHydrationDataExtractor`

The main class for extracting Next.js hydration data.

#### Methods

- **`parse(html_content: str, lightweight: bool = False, target_patterns: Optional[List[str]] = None) -> List[Dict[str, Any]]`**
  
  Parse Next.js hydration data from HTML content.
  
  - `html_content`: Raw HTML string containing script tags
  - `lightweight`: If True, only process chunks containing target patterns (much faster)
  - `target_patterns`: List of strings to search for in lightweight mode (e.g., `["products", "listings"]`)
  - Returns: List of parsed data chunks

- **`parse_and_find(html_content: str, patterns: List[str]) -> List[Any]`** ⚡ **RECOMMENDED**
  
  Convenience method that combines lightweight parsing with pattern matching. Much faster than full parsing when you know what you're looking for.
  
  - `html_content`: Raw HTML string
  - `patterns`: List of key patterns to search for (e.g., `["products", "catalog", "items"]`)
  - Returns: List of matching data items with their paths and values
  - **Performance**: 10-15x faster than full parsing on large pages

- **`get_all_keys(parsed_chunks: List[Dict], max_depth: int = 3) -> Dict[str, int]`**
  
  Extract all unique keys from parsed chunks.
  
  - `parsed_chunks`: Output from `parse()` method
  - `max_depth`: Maximum depth to traverse
  - Returns: Dictionary of keys and their occurrence counts

- **`find_data_by_pattern(parsed_chunks: List[Dict], pattern: str) -> List[Any]`**
  
  Find data matching a specific pattern.
  
  - `parsed_chunks`: Output from `parse()` method  
  - `pattern`: Key pattern to search for
  - Returns: List of matching data items

## Data Structure

The parser returns data in the following structure:

```python
[
    {
        "chunk_id": "1",  # ID from self.__next_f.push([ID, data])
        "extracted_data": [
            {
                "type": "colon_separated|standalone_json|whole_text",
                "data": {...},  # Parsed JavaScript/JSON object
                "identifier": "...",  # For colon_separated type
                "start_position": 123  # For standalone_json type
            }
        ],
        "chunk_count": 1,  # Number of chunks with this ID
        "_positions": [123]  # Original positions in HTML
    }
]
```

## Supported Data Formats

The parser handles various data formats commonly found in Next.js 13+ hydration chunks:

### 1. JSON Strings
```javascript
self.__next_f.push([1, "{\"products\":[{\"id\":1,\"name\":\"Laptop\",\"price\":999}]}"])
```

### 2. Base64 + JSON Combinations  
```javascript
self.__next_f.push([2, "eyJhcGlLZXkiOiJ4eXoifQ==:{\"data\":{\"users\":[{\"id\":1}]}}"])
```

### 3. JavaScript Objects
```javascript
self.__next_f.push([3, "{key: 'value', items: [1, 2, 3], nested: {deep: true}}"])
```

### 4. Escaped Content
```javascript  
self.__next_f.push([4, "\"escaped content with \\\"quotes\\\" and newlines\\n\""])
```

### 5. Multi-chunk Data
```javascript
// Data split across multiple chunks with same ID
self.__next_f.push([5, "first part of data"])
self.__next_f.push([5, " continued here"])
self.__next_f.push([5, " and final part"])
```

### 6. Complex Nested Structures
Next.js often embeds API responses, page props, and component data in deeply nested formats that the parser can extract and flatten for easy access.

## How Next.js 13+ Hydration Works

Understanding the hydration process helps explain why this library is necessary:

1. **Server-Side Rendering**: Next.js renders your page on the server, generating static HTML
2. **Data Embedding**: Instead of making separate API calls, Next.js may embeds the data directly in the HTML using `self.__next_f.push()` calls
3. **Chunk Splitting**: Large data sets are split across multiple chunks to optimize loading
4. **Client Hydration**: When JavaScript loads, these chunks are reassembled and used to hydrate React components

When scraping, you're intercepting step 2 - getting the raw HTML with embedded data before the JavaScript processes it. This gives you access to all the data the application uses, but in a fragmented format that needs intelligent parsing.

**Why not just use the rendered page?** 
- Faster scraping (no JavaScript execution wait time)
- Access to internal data structures not visible in the DOM
- Bypasses client-side anti-scraping measures
- Gets raw API responses before component filtering/transformation

## Error Handling

The parser includes robust error handling:

- **Malformed data**: Continues processing and marks chunks with errors
- **Multiple parsing strategies**: Falls back to alternative parsing methods
- **Partial data**: Handles incomplete or truncated data gracefully

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/kennyaires/nextjs-hydration-parser.git
cd nextjs-hydration-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with testing dependencies
pip install -e .[dev]

# Run tests
pytest tests/ -v

# Run formatting
black nextjs_hydration_parser/ tests/

# Test with real Next.js sites
python examples/scrape_example.py
```

### Testing with Real Sites

The library includes examples for testing with popular Next.js sites:

```bash
# Test with different types of Next.js applications
python examples/test_ecommerce.py
python examples/test_blog.py  
python examples/test_social.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

This project is not affiliated with or endorsed by Vercel, Next.js, or any related entity.  
All trademarks and brand names are the property of their respective owners.

This library is intended for ethical use only. Users are solely responsible for ensuring that their use of this software complies with applicable laws, website terms of service, and data usage policies. The authors disclaim any liability for misuse or violations resulting from the use of this tool.

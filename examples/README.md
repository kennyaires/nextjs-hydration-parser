# Examples Directory

This directory contains examples demonstrating the capabilities of the Next.js Hydration Parser.

## Available Examples

### 1. `basic_usage.py`
**Basic functionality demonstration**
- Shows how to create an extractor instance
- Demonstrates parsing simple hydration data
- Shows search functionality for finding specific patterns
- Good starting point for understanding the library

**Run with:** `python examples/basic_usage.py`

### 2. `ecommerce_scraping.py`
**E-commerce data extraction**
- Simulates parsing an e-commerce website
- Extracts product catalogs, categories, user data, and cart information
- Demonstrates data analysis and organization
- Shows how to handle realistic business data

**Run with:** `python examples/ecommerce_scraping.py`

### 3. `real_world_scraping.py`
**Real-world scraping with requests**
- Shows how to scrape actual websites using the `requests` library
- Includes proper headers and rate limiting
- Demonstrates analysis of scraped data
- Includes examples for testing with known Next.js sites
- **Interactive mode:** Lets you test custom URLs

**Run with:** `python examples/real_world_scraping.py`

### 4. `advanced_features.py`
**Advanced parsing features**
- Complex nested data structures
- Error handling and recovery
- Multi-chunk data assembly
- Custom pattern searching
- Performance testing with large datasets

**Run with:** `python examples/advanced_features.py`

### 5. `sample_html_analysis.py`
**Sample HTML file analysis**
- Parses the included `sample_nextjs_page.html` file
- Comprehensive analysis of realistic e-commerce data
- Demonstrates key extraction and pattern matching
- Shows various data types and formats

**Run with:** `python examples/sample_html_analysis.py`

## Sample Data

### `sample_nextjs_page.html`
A realistic Next.js e-commerce page with comprehensive hydration data including:
- Product catalogs with detailed specifications
- Category navigation and filters
- User session and shopping cart data
- Recommendations and analytics
- Multi-chunk data examples
- Various data formats (JSON, base64, JavaScript objects)

This file serves as a testing ground for understanding how the parser works with real-world data.

## Running Examples

### Run All Examples
```bash
python run_examples.py
```

### Run Examples Interactively
```bash
python run_examples.py --interactive
```

### Run Individual Examples
```bash
python examples/basic_usage.py
python examples/ecommerce_scraping.py
python examples/sample_html_analysis.py
```

## Example Output

Each example provides detailed output showing:
- Number of chunks found
- Data types discovered
- Analysis of extracted information
- Sample data previews
- Performance metrics (where applicable)

## Prerequisites

Most examples only require the base library dependencies:
- `chompjs` (for JavaScript object parsing)

The `real_world_scraping.py` example additionally requires:
- `requests` (for web scraping)

Install development dependencies with:
```bash
pip install -r requirements-dev.txt
```

## Usage Tips

1. **Start with `basic_usage.py`** to understand core concepts
2. **Use `sample_html_analysis.py`** to see comprehensive parsing on realistic data
3. **Try `ecommerce_scraping.py`** for business use case examples
4. **Experiment with `real_world_scraping.py`** for actual website testing
5. **Explore `advanced_features.py`** for complex scenarios

## Creating Your Own Examples

When creating new examples:
1. Follow the existing pattern of using docstrings to describe functionality
2. Include error handling for missing dependencies
3. Provide clear output with section headers
4. Show both successful parsing and edge cases
5. Add your example to this README

## Contributing

If you have interesting use cases or examples, please consider contributing them back to the project!

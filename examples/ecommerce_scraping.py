#!/usr/bin/env python3
"""
E-commerce scraping example using Next.js Hydration Parser

This example demonstrates how to extract product data from
a simulated Next.js e-commerce site.
"""

import json
from nextjs_hydration_parser import NextJSHydrationDataExtractor


def simulate_ecommerce_html():
    """Generate sample HTML that mimics a real Next.js e-commerce site"""

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NextShop - Electronics</title>
    </head>
    <body>
        <div id="__next">
            <h1>Product Catalog</h1>
            <div class="products-grid">Loading...</div>
        </div>
        
        <!-- Next.js hydration data -->
        <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Gaming Laptop\\",\\"price\\":1299.99,\\"currency\\":\\"USD\\",\\"inStock\\":true,\\"category\\":\\"laptops\\",\\"brand\\":\\"TechBrand\\",\\"rating\\":4.5,\\"reviews\\":127}]}"])</script>
        <script>self.__next_f.push([1,",{\\"id\\":2,\\"name\\":\\"Wireless Mouse\\",\\"price\\":29.99,\\"currency\\":\\"USD\\",\\"inStock\\":false,\\"category\\":\\"accessories\\",\\"brand\\":\\"MouseCorp\\",\\"rating\\":4.2,\\"reviews\\":89}]}"])</script>
        <script>self.__next_f.push([2,"{\\"categories\\":[{\\"id\\":1,\\"name\\":\\"Laptops\\",\\"count\\":45},{\\"id\\":2,\\"name\\":\\"Accessories\\",\\"count\\":123},{\\"id\\":3,\\"name\\":\\"Monitors\\",\\"count\\":67}]}"])</script>
        <script>self.__next_f.push([3,"{\\"user\\":{\\"id\\":12345,\\"cart\\":{\\"items\\":[{\\"productId\\":1,\\"quantity\\":1}],\\"total\\":1299.99},\\"wishlist\\":[2,15,23]}}"])</script>
        <script>self.__next_f.push([4,"{\\"filters\\":{\\"priceRange\\":{\\"min\\":0,\\"max\\":2000},\\"brands\\":[\\"TechBrand\\",\\"MouseCorp\\",\\"ScreenMaster\\"],\\"inStockOnly\\":false}}"])</script>
        <script>self.__next_f.push([5,"api_data:{\\"recommendations\\":[{\\"id\\":15,\\"name\\":\\"4K Monitor\\",\\"price\\":399.99,\\"reason\\":\\"frequently_bought_together\\"}]}"])</script>
    </body>
    </html>
    """


def extract_product_data(html_content):
    """Extract and organize product data from HTML"""

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    # Organize extracted data
    extracted_data = {
        "products": [],
        "categories": [],
        "user_data": {},
        "filters": {},
        "recommendations": [],
    }

    for chunk in chunks:
        if chunk["chunk_id"] == "error":
            print(
                f"Warning: Found error chunk - {chunk.get('_error', 'Unknown error')}"
            )
            continue

        for item in chunk["extracted_data"]:
            data = item["data"]

            if isinstance(data, dict):
                # Direct data extraction
                if "products" in data:
                    extracted_data["products"].extend(data["products"])
                if "categories" in data:
                    extracted_data["categories"].extend(data["categories"])
                if "user" in data:
                    extracted_data["user_data"].update(data["user"])
                if "filters" in data:
                    extracted_data["filters"].update(data["filters"])

            elif item["type"] == "colon_separated":
                # Handle API data format
                identifier = item.get("identifier", "")
                if "api" in identifier.lower() and isinstance(data, dict):
                    if "recommendations" in data:
                        extracted_data["recommendations"].extend(
                            data["recommendations"]
                        )

    return extracted_data


def analyze_products(product_data):
    """Analyze extracted product data"""

    products = product_data["products"]

    print(f"=== Product Analysis ===")
    print(f"Total products found: {len(products)}")

    if products:
        # Price analysis
        prices = [p["price"] for p in products if "price" in p]
        if prices:
            print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            print(f"Average price: ${sum(prices)/len(prices):.2f}")

        # Stock analysis
        in_stock = len([p for p in products if p.get("inStock", False)])
        print(f"In stock: {in_stock}/{len(products)} products")

        # Brand analysis
        brands = {}
        for product in products:
            brand = product.get("brand", "Unknown")
            brands[brand] = brands.get(brand, 0) + 1
        print(f"Brands: {dict(brands)}")

        # Category analysis
        categories = {}
        for product in products:
            category = product.get("category", "Unknown")
            categories[category] = categories.get(category, 0) + 1
        print(f"Categories: {dict(categories)}")


def analyze_user_behavior(product_data):
    """Analyze user behavior data"""

    user_data = product_data["user_data"]

    print(f"\n=== User Behavior Analysis ===")

    if "cart" in user_data:
        cart = user_data["cart"]
        print(f"Cart items: {len(cart.get('items', []))}")
        print(f"Cart total: ${cart.get('total', 0):.2f}")

    if "wishlist" in user_data:
        wishlist = user_data["wishlist"]
        print(f"Wishlist items: {len(wishlist)}")

    recommendations = product_data["recommendations"]
    if recommendations:
        print(f"Recommendations: {len(recommendations)} items")
        for rec in recommendations:
            print(f"  - {rec['name']}: ${rec['price']} ({rec.get('reason', 'N/A')})")


def main():
    """Main example function"""

    print("E-commerce Scraping Example")
    print("=" * 40)

    # Get sample HTML
    html_content = simulate_ecommerce_html()
    print(f"HTML content length: {len(html_content)} characters")

    # Extract data
    product_data = extract_product_data(html_content)

    # Analyze results
    analyze_products(product_data)
    analyze_user_behavior(product_data)

    # Show raw data sample
    print(f"\n=== Raw Data Sample ===")
    if product_data["products"]:
        print("First product:")
        print(json.dumps(product_data["products"][0], indent=2))

    print(f"\nCategories found:")
    for category in product_data["categories"]:
        print(f"  - {category['name']}: {category['count']} items")


if __name__ == "__main__":
    main()

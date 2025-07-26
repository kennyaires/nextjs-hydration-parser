#!/usr/bin/env python3
"""
Basic usage example for Next.js Hydration Parser

This example demonstrates the basic functionality of extracting
hydration data from Next.js HTML content.
"""

from nextjs_hydration_parser import NextJSHydrationDataExtractor


def basic_example():
    """Demonstrate basic parsing functionality"""

    # Sample HTML content with Next.js hydration data
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Next.js Page</title>
    </head>
    <body>
        <div id="__next">Content here</div>
        
        <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Laptop\\",\\"price\\":999}]}"])</script>
        <script>self.__next_f.push([2,"{\\"users\\":[{\\"id\\":1,\\"name\\":\\"John\\",\\"email\\":\\"john@example.com\\"}]}"])</script>
        <script>self.__next_f.push([3,"base64data:{\\"api_response\\":{\\"status\\":\\"success\\",\\"data\\":[1,2,3]}}"])</script>
        <script>self.__next_f.push([1," continuation of products data"])</script>
    </body>
    </html>
    """

    # Create extractor and parse
    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("=== Basic Parsing Results ===")
    print(f"Found {len(chunks)} hydration chunks")

    for chunk in chunks:
        print(f"\nChunk ID: {chunk['chunk_id']}")
        print(f"Number of data items: {len(chunk['extracted_data'])}")
        print(f"Chunk count: {chunk['chunk_count']}")

        for i, item in enumerate(chunk["extracted_data"]):
            print(f"  Item {i+1}:")
            print(f"    Type: {item['type']}")
            if item["type"] == "colon_separated":
                print(f"    Identifier: {item.get('identifier', 'N/A')}")
            print(f"    Data preview: {str(item['data'])[:100]}...")


def search_example():
    """Demonstrate search functionality"""

    html_content = """
    <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Gaming Laptop\\",\\"price\\":1299,\\"category\\":\\"electronics\\"}]}"])</script>
    <script>self.__next_f.push([2,"{\\"categories\\":[{\\"id\\":1,\\"name\\":\\"Electronics\\"},{\\"id\\":2,\\"name\\":\\"Books\\"}]}"])</script>
    <script>self.__next_f.push([3,"{\\"user\\":{\\"id\\":123,\\"preferences\\":{\\"theme\\":\\"dark\\",\\"language\\":\\"en\\"}}}"])</script>
    """

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("\n=== Search Examples ===")

    # Get all available keys
    all_keys = extractor.get_all_keys(chunks)
    print(f"All available keys: {list(all_keys.keys())}")

    # Search for specific patterns
    products = extractor.find_data_by_pattern(chunks, "products")
    print(f"\nFound {len(products)} items matching 'products':")
    for item in products:
        print(f"  Path: {item.get('path', 'N/A')}")
        print(f"  Value: {item['value']}")

    # Search for user data
    user_data = extractor.find_data_by_pattern(chunks, "user")
    print(f"\nFound {len(user_data)} items matching 'user':")
    for item in user_data:
        print(f"  Value: {item['value']}")


if __name__ == "__main__":
    basic_example()
    search_example()

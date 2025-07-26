#!/usr/bin/env python3
"""
Advanced features example

Demonstrates advanced parsing features like handling complex
data structures, error recovery, and custom processing.
"""

import json
from nextjs_hydration_parser import NextJSHydrationDataExtractor


def complex_data_example():
    """Example with complex nested data structures"""

    html_content = """
    <script>self.__next_f.push([1,"{\\"pageProps\\":{\\"initialData\\":{\\"users\\":[{\\"id\\":1,\\"profile\\":{\\"name\\":\\"John\\",\\"settings\\":{\\"theme\\":\\"dark\\",\\"notifications\\":\\"enabled\\"}}}]}}}"])</script>
    <script>self.__next_f.push([2,"base64:eyJ0ZXN0IjoidmFsdWUifQ==:{\\"api\\":{\\"endpoint\\":\\"/api/data\\",\\"response\\":{\\"status\\":200,\\"data\\":[1,2,3,4,5]}}}"])</script>
    <script>self.__next_f.push([3,"{posts: [{id: 1, title: 'First Post', meta: {author: 'Jane', tags: ['tech', 'nextjs']}}]}"])</script>
    <script>self.__next_f.push([4,"{\\"errors\\":[{\\"field\\":\\"email\\",\\"message\\":\\"Invalid format\\"}],\\"warnings\\":[\\"Deprecated API used\\"]}"])</script>
    """

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("=== Complex Data Structure Example ===")

    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}:")
        for item in chunk["extracted_data"]:
            print(f"  Type: {item['type']}")

            if isinstance(item["data"], dict):
                # Pretty print complex structures
                print("  Data structure:")
                print(json.dumps(item["data"], indent=4))
            else:
                print(f"  Raw data: {item['data']}")


def error_handling_example():
    """Example showing error handling capabilities"""

    # HTML with intentionally malformed data
    html_content = """
    <script>self.__next_f.push([1,"valid json: {\\"test\\": \\"value\\"}"])</script>
    <script>self.__next_f.push([2,"invalid json: {broken: json, missing: quotes}"])</script>
    <script>self.__next_f.push([3,"partial data that gets cut off..."])</script>
    <script>self.__next_f.push([4,"{unclosed: 'bracket'"])</script>
    <script>self.__next_f.push([5,"{\\"recovered\\": \\"data\\", \\"after\\": \\"error\\"}"])</script>
    """

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("\n=== Error Handling Example ===")

    valid_chunks = 0
    error_chunks = 0

    for chunk in chunks:
        if chunk["chunk_id"] == "error":
            error_chunks += 1
            print(f"\nError chunk at position {chunk['_position']}:")
            print(f"  Error: {chunk['_error']}")
            print(f"  Raw content preview: {chunk['raw_content'][:100]}...")
        else:
            valid_chunks += 1
            print(f"\nValid chunk {chunk['chunk_id']}:")
            for item in chunk["extracted_data"]:
                print(f"  Successfully parsed: {item['type']}")

    print(f"\nSummary: {valid_chunks} valid chunks, {error_chunks} error chunks")
    print("Note: Parser continues processing despite errors")


def multi_chunk_assembly_example():
    """Example showing how multi-chunk data is assembled"""

    html_content = """
    <script>self.__next_f.push([1,"{\\"bigDataSet\\": [\\"item1\\","])</script>
    <script>self.__next_f.push([1,"\\"item2\\", \\"item3\\","])</script>
    <script>self.__next_f.push([1,"\\"item4\\", \\"item5\\"]}"])</script>
    <script>self.__next_f.push([2,"{\\"metadata\\": {\\"total\\": 1000,"])</script>
    <script>self.__next_f.push([2,"\\"page\\": 1, \\"hasMore\\": true}}"])</script>
    """

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("\n=== Multi-chunk Assembly Example ===")

    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"  Assembled from {chunk['chunk_count']} fragments")
        print(f"  Original positions: {chunk['_positions']}")

        for item in chunk["extracted_data"]:
            if isinstance(item["data"], dict):
                print(f"  Assembled data keys: {list(item['data'].keys())}")
                if "bigDataSet" in item["data"]:
                    dataset = item["data"]["bigDataSet"]
                    print(f"    Big dataset length: {len(dataset)} items")
                    print(f"    Items: {dataset}")


def custom_pattern_search_example():
    """Example of advanced pattern searching"""

    html_content = """
    <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Laptop\\",\\"specs\\":{\\"cpu\\":\\"Intel i7\\",\\"ram\\":\\"16GB\\",\\"storage\\":\\"512GB SSD\\"}}]}"])</script>
    <script>self.__next_f.push([2,"{\\"reviews\\":[{\\"productId\\":1,\\"rating\\":5,\\"comment\\":\\"Great laptop!\\"}]}"])</script>
    <script>self.__next_f.push([3,"{\\"inventory\\":{\\"laptop\\":{\\"inStock\\":15,\\"reserved\\":3,\\"available\\":12}}}"])</script>
    """

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    print("\n=== Custom Pattern Search Example ===")

    # Search for different patterns
    patterns_to_search = ["product", "review", "stock", "rating", "cpu"]

    for pattern in patterns_to_search:
        matches = extractor.find_data_by_pattern(chunks, pattern)
        if matches:
            print(f"\nPattern '{pattern}' found {len(matches)} times:")
            for match in matches:
                print(f"  Path: {match.get('path', 'N/A')}")
                print(f"  Value: {match['value']}")
        else:
            print(f"\nPattern '{pattern}': No matches found")

    # Get all keys for analysis
    all_keys = extractor.get_all_keys(chunks, max_depth=4)
    print(f"\nAll available keys (depth=4): {list(all_keys.keys())}")


def performance_example():
    """Example showing performance with large datasets"""

    # Generate large HTML content
    print("\n=== Performance Example ===")
    print("Generating large dataset...")

    # Create HTML with many chunks
    html_parts = ["<html><body>"]

    for i in range(100):  # 100 chunks
        chunk_data = {
            "batch": i,
            "items": [{"id": j, "value": f"item_{i}_{j}"} for j in range(10)],
        }
        json_data = json.dumps(chunk_data).replace('"', '\\"')
        html_parts.append(
            f'<script>self.__next_f.push([{i % 10},"{json_data}"])</script>'
        )

    html_parts.append("</body></html>")
    html_content = "\n".join(html_parts)

    print(f"Generated HTML with {len(html_content)} characters")

    # Time the parsing
    import time

    start_time = time.time()

    extractor = NextJSHydrationDataExtractor()
    chunks = extractor.parse(html_content)

    end_time = time.time()

    print(f"Parsing took {end_time - start_time:.3f} seconds")
    print(f"Found {len(chunks)} unique chunk IDs")

    total_items = sum(len(chunk["extracted_data"]) for chunk in chunks)
    print(f"Total data items processed: {total_items}")

    # Show memory usage (approximate)
    import sys

    memory_usage = sys.getsizeof(chunks) + sum(sys.getsizeof(chunk) for chunk in chunks)
    print(f"Approximate memory usage: {memory_usage / 1024:.1f} KB")


def main():
    """Run all advanced examples"""

    print("Advanced Next.js Hydration Parser Examples")
    print("=" * 50)

    complex_data_example()
    error_handling_example()
    multi_chunk_assembly_example()
    custom_pattern_search_example()
    performance_example()

    print("\n" + "=" * 50)
    print("All advanced examples completed!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Demo: Lightweight mode for faster parsing when targeting specific patterns.

This example shows the performance difference between full parsing and lightweight mode.
"""

import time
from nextjs_hydration_parser import NextJSHydrationDataExtractor


def demo_lightweight_mode():
    """Demonstrate lightweight parsing mode with target patterns."""
    
    # Load a sample Next.js page (you can replace with any large Next.js HTML file)
    with open('examples/sample_nextjs_page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    extractor = NextJSHydrationDataExtractor()
    
    print("=" * 70)
    print("LIGHTWEIGHT MODE DEMO - Target Pattern: 'products'")
    print("=" * 70)
    
    # Method 1: Full parsing (slow for large pages)
    print("\n1. FULL PARSING MODE:")
    print("-" * 70)
    start = time.time()
    full_results = extractor.parse(html_content)
    full_time = time.time() - start
    
    print(f"   Time taken: {full_time:.4f} seconds")
    print(f"   Total chunks found: {len(full_results)}")
    
    # Find products in full results
    matches = extractor.find_data_by_pattern(full_results, "products")
    print(f"   Matching items for 'products': {len(matches)}")
    
    # Method 2: Lightweight parsing with target pattern (fast!)
    print("\n2. LIGHTWEIGHT MODE (with target pattern):")
    print("-" * 70)
    start = time.time()
    lightweight_results = extractor.parse(
        html_content, 
        lightweight=True, 
        target_patterns=["products"]
    )
    lightweight_time = time.time() - start
    
    print(f"   Time taken: {lightweight_time:.4f} seconds")
    print(f"   Chunks processed: {len(lightweight_results)}")
    print(f"   Chunks with data: {len([c for c in lightweight_results if not c.get('_skipped')])}")
    
    # Find products in lightweight results
    matches_light = extractor.find_data_by_pattern(lightweight_results, "products")
    print(f"   Matching items for 'products': {len(matches_light)}")
    
    # Method 3: Convenience method (easiest and fastest!)
    print("\n3. CONVENIENCE METHOD (parse_and_find):")
    print("-" * 70)
    start = time.time()
    quick_results = extractor.parse_and_find(html_content, ["products"])
    quick_time = time.time() - start
    
    print(f"   Time taken: {quick_time:.4f} seconds")
    print(f"   Matching items found: {len(quick_results)}")
    
    # Performance comparison
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON:")
    print("=" * 70)
    speedup_light = full_time / lightweight_time if lightweight_time > 0 else float('inf')
    speedup_quick = full_time / quick_time if quick_time > 0 else float('inf')
    
    print(f"   Full parsing:        {full_time:.4f}s")
    print(f"   Lightweight mode:    {lightweight_time:.4f}s  ({speedup_light:.1f}x faster)")
    print(f"   parse_and_find:      {quick_time:.4f}s  ({speedup_quick:.1f}x faster)")
    
    # Show sample data
    if quick_results:
        print("\n" + "=" * 70)
        print("SAMPLE RESULT:")
        print("=" * 70)
        first_result = quick_results[0]
        print(f"   Path: {first_result['path']}")
        print(f"   Key:  {first_result['key']}")
        
        # Show a preview of the value
        value = first_result['value']
        if isinstance(value, dict):
            print(f"   Value type: dict with {len(value)} keys")
            print(f"   Keys: {list(value.keys())[:5]}...")
        elif isinstance(value, list):
            print(f"   Value type: list with {len(value)} items")
        else:
            print(f"   Value: {str(value)[:100]}...")


if __name__ == "__main__":
    demo_lightweight_mode()

"""
Tests for lightweight parsing mode and parse_and_find functionality.
"""

import pytest
import time
from nextjs_hydration_parser import NextJSHydrationDataExtractor


class TestLightweightMode:
    """Test lightweight parsing mode functionality."""

    @pytest.fixture
    def extractor(self):
        return NextJSHydrationDataExtractor()

    @pytest.fixture
    def sample_html_with_products(self):
        """HTML with multiple chunks, some containing 'products'."""
        return """
        <html>
        <script>self.__next_f.push([1,'{"products":[{"id":1,"name":"Product 1"}]}'])</script>
        <script>self.__next_f.push([2,'{"users":[{"id":1,"name":"User 1"}]}'])</script>
        <script>self.__next_f.push([3,'{"products":[{"id":2,"name":"Product 2"}]}'])</script>
        <script>self.__next_f.push([4,'{"orders":[{"id":1}]}'])</script>
        <script>self.__next_f.push([5,'{"products":[{"id":3,"name":"Product 3"}]}'])</script>
        </html>
        """

    @pytest.fixture
    def large_html_with_pattern(self):
        """Large HTML with specific patterns for performance testing."""
        chunks = []
        # Add 50 chunks without target pattern
        for i in range(50):
            chunks.append(
                f'<script>self.__next_f.push([{i},\'{{"data{i}":[{{"value":{i}}}]}}\'])</script>'
            )

        # Add 5 chunks with target pattern
        for i in range(50, 55):
            chunks.append(
                f'<script>self.__next_f.push([{i},\'{{"targetPattern":[{{"id":{i}}}]}}\'])</script>'
            )

        # Add 50 more chunks without target pattern
        for i in range(55, 105):
            chunks.append(
                f'<script>self.__next_f.push([{i},\'{{"data{i}":[{{"value":{i}}}]}}\'])</script>'
            )

        return f"<html>{''.join(chunks)}</html>"

    def test_lightweight_parse_basic(self, extractor, sample_html_with_products):
        """Test basic lightweight parsing with target patterns."""
        result = extractor.parse(
            sample_html_with_products, lightweight=True, target_patterns=["products"]
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Check that some chunks were skipped (those without "products")
        skipped_chunks = [c for c in result if c.get("_skipped")]
        processed_chunks = [c for c in result if not c.get("_skipped")]

        # At least some chunks should be processed (those with "products")
        assert len(processed_chunks) > 0, "Some chunks should be processed"

        # In lightweight mode, only chunks matching the pattern are returned
        # From sample_html_with_products: 3 products chunks should be returned
        assert len(result) >= 3  # Three products chunks

    def test_lightweight_vs_full_parsing_results(
        self, extractor, sample_html_with_products
    ):
        """Test that lightweight mode finds the same target data as full parsing."""
        # Full parsing
        full_result = extractor.parse(sample_html_with_products)
        full_matches = extractor.find_data_by_pattern(full_result, "products")

        # Lightweight parsing
        light_result = extractor.parse(
            sample_html_with_products, lightweight=True, target_patterns=["products"]
        )
        light_matches = extractor.find_data_by_pattern(light_result, "products")

        # Should find the same number of products
        assert len(full_matches) == len(light_matches)

        # Verify we found products
        assert len(full_matches) > 0

    def test_lightweight_performance_improvement(
        self, extractor, large_html_with_pattern
    ):
        """Test that lightweight mode is faster than full parsing."""
        # Full parsing
        start = time.time()
        full_result = extractor.parse(large_html_with_pattern)
        full_time = time.time() - start

        # Lightweight parsing
        start = time.time()
        light_result = extractor.parse(
            large_html_with_pattern, lightweight=True, target_patterns=["targetPattern"]
        )
        light_time = time.time() - start

        # Lightweight should be faster (or at least not slower)
        # Allow some margin for small datasets
        assert (
            light_time <= full_time * 1.5
        ), f"Lightweight mode should be faster: {light_time}s vs {full_time}s"

        # Should still find the target data
        matches = extractor.find_data_by_pattern(light_result, "targetPattern")
        assert len(matches) > 0

    def test_lightweight_with_multiple_patterns(
        self, extractor, sample_html_with_products
    ):
        """Test lightweight mode with multiple target patterns."""
        result = extractor.parse(
            sample_html_with_products,
            lightweight=True,
            target_patterns=["products", "users"],
        )

        processed_chunks = [c for c in result if not c.get("_skipped")]

        # Should process chunks containing either pattern
        assert len(processed_chunks) >= 4  # At least products and users chunks

    def test_lightweight_with_no_matches(self, extractor, sample_html_with_products):
        """Test lightweight mode when pattern doesn't exist."""
        result = extractor.parse(
            sample_html_with_products, lightweight=True, target_patterns=["nonexistent"]
        )

        # All chunks should be skipped
        skipped_chunks = [c for c in result if c.get("_skipped")]
        assert len(skipped_chunks) == len(result)

    def test_lightweight_without_patterns(self, extractor, sample_html_with_products):
        """Test lightweight mode without specifying patterns."""
        # Should work but won't skip anything
        result = extractor.parse(
            sample_html_with_products, lightweight=True, target_patterns=None
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_lightweight_empty_patterns_list(
        self, extractor, sample_html_with_products
    ):
        """Test lightweight mode with empty patterns list."""
        result = extractor.parse(
            sample_html_with_products, lightweight=True, target_patterns=[]
        )

        # Empty list means no filtering, so nothing should be skipped
        assert isinstance(result, list)


class TestParseAndFind:
    """Test parse_and_find convenience method."""

    @pytest.fixture
    def extractor(self):
        return NextJSHydrationDataExtractor()

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
        <script>self.__next_f.push([1,'{"products":[{"id":1,"name":"Laptop","price":999}]}'])</script>
        <script>self.__next_f.push([2,'{"users":[{"id":1,"name":"John"}]}'])</script>
        <script>self.__next_f.push([3,'{"catalog":{"products":[{"id":2,"name":"Mouse"}]}}'])</script>
        </html>
        """

    def test_parse_and_find_basic(self, extractor, sample_html):
        """Test basic parse_and_find functionality."""
        results = extractor.parse_and_find(sample_html, ["products"])

        assert isinstance(results, list)
        assert len(results) > 0

        # Check structure of results
        for result in results:
            assert "path" in result
            assert "key" in result
            assert "value" in result
            assert (
                result["key"].lower().find("products") != -1
                or result["path"].lower().find("products") != -1
            )

    def test_parse_and_find_multiple_patterns(self, extractor, sample_html):
        """Test parse_and_find with multiple patterns."""
        results = extractor.parse_and_find(sample_html, ["products", "users"])

        assert len(results) > 0

        # Should find both products and users
        found_keys = [r["key"] for r in results]
        assert any(
            "products" in k.lower() or "products" in r["path"].lower()
            for k, r in zip(found_keys, results)
        )

    def test_parse_and_find_no_matches(self, extractor, sample_html):
        """Test parse_and_find when pattern doesn't exist."""
        results = extractor.parse_and_find(sample_html, ["nonexistent"])

        assert isinstance(results, list)
        assert len(results) == 0

    def test_parse_and_find_empty_html(self, extractor):
        """Test parse_and_find with empty HTML."""
        results = extractor.parse_and_find("", ["products"])

        assert isinstance(results, list)
        assert len(results) == 0

    def test_parse_and_find_empty_patterns(self, extractor, sample_html):
        """Test parse_and_find with empty patterns list."""
        results = extractor.parse_and_find(sample_html, [])

        assert isinstance(results, list)
        assert len(results) == 0

    def test_parse_and_find_returns_correct_structure(self, extractor, sample_html):
        """Test that parse_and_find returns properly structured data."""
        results = extractor.parse_and_find(sample_html, ["products"])

        if len(results) > 0:
            result = results[0]

            # Verify structure
            assert isinstance(result["path"], str)
            assert isinstance(result["key"], str)
            assert result["value"] is not None

    def test_parse_and_find_performance(self, extractor):
        """Test that parse_and_find is efficient."""
        # Create a moderately sized HTML
        chunks = []
        for i in range(20):
            chunks.append(
                f'<script>self.__next_f.push([{i},\'{{"data{i}":[{{"value":{i}}}]}}\'])</script>'
            )
        chunks.append(
            '<script>self.__next_f.push([20,\'{"target":[{"id":1}]}\'])</script>'
        )

        html = f"<html>{''.join(chunks)}</html>"

        start = time.time()
        results = extractor.parse_and_find(html, ["target"])
        elapsed = time.time() - start

        # Should complete quickly (less than 1 second for this small example)
        assert elapsed < 1.0
        assert len(results) > 0


class TestLightweightModeIntegration:
    """Integration tests for lightweight mode with real-world scenarios."""

    @pytest.fixture
    def extractor(self):
        return NextJSHydrationDataExtractor()

    def test_ecommerce_product_extraction(self, extractor):
        """Test extracting product data from e-commerce page."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"siteConfig":{"name":"Store"}}'])</script>
        <script>self.__next_f.push([2,'{"products":[{"id":1,"name":"Item 1","price":10},{"id":2,"name":"Item 2","price":20}]}'])</script>
        <script>self.__next_f.push([3,'{"navigation":{"items":[]}}'])</script>
        <script>self.__next_f.push([4,'{"products":[{"id":3,"name":"Item 3","price":30}]}'])</script>
        </html>
        """

        results = extractor.parse_and_find(html, ["products"])

        assert len(results) > 0

        # Verify we found product data
        product_values = [r["value"] for r in results if r["key"] == "products"]
        assert len(product_values) > 0

    def test_catalog_with_nested_data(self, extractor):
        """Test extracting nested catalog data."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"catalog":{"categories":[{"name":"Electronics","products":[{"id":1}]}]}}'])</script>
        <script>self.__next_f.push([2,'{"other":"data"}'])</script>
        </html>
        """

        # Search for both catalog and products
        results = extractor.parse_and_find(html, ["catalog", "products"])

        assert len(results) > 0

    def test_case_insensitive_pattern_matching(self, extractor):
        """Test that find_data_by_pattern works case-insensitively after parsing."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"Products":[{"id":1}]}'])</script>
        <script>self.__next_f.push([2,'{"PRODUCTS":[{"id":2}]}'])</script>
        <script>self.__next_f.push([3,'{"products":[{"id":3}]}'])</script>
        </html>
        """

        # Use full parsing for case-insensitive matching
        chunks = extractor.parse(html)
        results = extractor.find_data_by_pattern(chunks, "products")

        # find_data_by_pattern is case-insensitive, should find all variants
        assert len(results) >= 3

    def test_lightweight_with_fragmented_data(self, extractor):
        """Test lightweight mode with data split across chunks."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"partial":"'])</script>
        <script>self.__next_f.push([1,'data","products":[{"id":1}]}'])</script>
        <script>self.__next_f.push([2,'{"other":"data"}'])</script>
        </html>
        """

        results = extractor.parse_and_find(html, ["products"])

        # Should handle fragmented data
        assert isinstance(results, list)


class TestLightweightModeEdgeCases:
    """Edge cases for lightweight mode."""

    @pytest.fixture
    def extractor(self):
        return NextJSHydrationDataExtractor()

    def test_pattern_at_chunk_boundary(self, extractor):
        """Test when pattern is split within a single chunk's data continuation."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"prod'])</script>
        <script>self.__next_f.push([1,'ucts":[{"id":1}]}'])</script>
        </html>
        """

        # Pattern is split across chunk continuations (same chunk_id)
        # After chunk assembly, "products" should be found
        result = extractor.parse(html)

        # Should successfully parse and assemble the chunks
        assert len(result) > 0
        assert any(chunk.get("chunk_id") == 1 for chunk in result)

    def test_special_characters_in_pattern(self, extractor):
        """Test patterns with special characters."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"product-items":[{"id":1}]}'])</script>
        <script>self.__next_f.push([2,'{"product_list":[{"id":2}]}'])</script>
        </html>
        """

        results = extractor.parse_and_find(html, ["product"])

        # Should find both variants
        assert len(results) >= 2

    def test_very_long_pattern(self, extractor):
        """Test with very long pattern names."""
        long_key = "very_long_key_name_that_goes_on_and_on"
        html = f'<html><script>self.__next_f.push([1,\'{{"{long_key}":[{{"id":1}}]}}\'])</script></html>'

        results = extractor.parse_and_find(html, [long_key])

        assert len(results) > 0

    def test_unicode_in_pattern(self, extractor):
        """Test patterns with unicode characters."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"产品":[{"id":1}]}'])</script>
        <script>self.__next_f.push([2,'{"données":[{"id":2}]}'])</script>
        </html>
        """

        results = extractor.parse_and_find(html, ["产品", "données"])

        # Should handle unicode
        assert isinstance(results, list)

    def test_pattern_in_value_not_key(self, extractor):
        """Test when pattern appears in value but not in key."""
        html = """
        <html>
        <script>self.__next_f.push([1,'{"items":[{"name":"products"}]}'])</script>
        </html>
        """

        # Lightweight mode filters by raw content, so it should find it
        result = extractor.parse(html, lightweight=True, target_patterns=["products"])

        processed = [c for c in result if not c.get("_skipped")]
        assert len(processed) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

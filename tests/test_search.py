"""
Tests for search and analysis functionality
"""

import pytest


class TestKeyExtraction:
    """Test key extraction functionality"""

    def test_get_all_keys_simple(self, extractor, simple_html):
        """Test key extraction from simple data"""
        chunks = extractor.parse(simple_html)
        keys = extractor.get_all_keys(chunks)

        assert isinstance(keys, dict)
        assert "test" in keys
        assert keys["test"] >= 1

    def test_get_all_keys_complex(self, extractor, complex_html):
        """Test key extraction from complex data"""
        chunks = extractor.parse(complex_html)
        keys = extractor.get_all_keys(chunks, max_depth=3)

        assert isinstance(keys, dict)
        assert len(keys) > 0

        # Should find some expected keys
        expected_keys = ["products", "users", "response", "status"]
        found_keys = list(keys.keys())

        # At least some expected keys should be found
        common_keys = set(expected_keys) & set(found_keys)
        assert (
            len(common_keys) > 0
        ), f"Should find some expected keys. Found: {found_keys}"

    def test_get_all_keys_max_depth(self, extractor):
        """Test max_depth parameter in key extraction"""
        html = """
        <script>self.__next_f.push([1,"{\\"level1\\": {\\"level2\\": {\\"level3\\": {\\"level4\\": \\"deep_value\\"}}}}"])</script>
        """

        chunks = extractor.parse(html)

        # Test different depths
        keys_depth_1 = extractor.get_all_keys(chunks, max_depth=1)
        keys_depth_3 = extractor.get_all_keys(chunks, max_depth=3)

        assert "level1" in keys_depth_1
        assert len(keys_depth_3) >= len(keys_depth_1)

    def test_get_all_keys_empty_chunks(self, extractor):
        """Test key extraction from empty chunks"""
        keys = extractor.get_all_keys([])
        assert keys == {}

    def test_key_counting(self, extractor):
        """Test that keys are counted correctly"""
        html = """
        <script>self.__next_f.push([1,"{\\"common_key\\": \\"value1\\"}"])</script>
        <script>self.__next_f.push([2,"{\\"common_key\\": \\"value2\\", \\"unique_key\\": \\"value3\\"}"])</script>
        """

        chunks = extractor.parse(html)
        keys = extractor.get_all_keys(chunks)

        assert keys["common_key"] == 2  # Appears in both chunks
        assert keys["unique_key"] == 1  # Appears in one chunk


class TestPatternSearch:
    """Test pattern search functionality"""

    def test_find_data_by_pattern_simple(self, extractor, ecommerce_html):
        """Test finding data by simple pattern"""
        chunks = extractor.parse(ecommerce_html)

        # Search for products
        products = extractor.find_data_by_pattern(chunks, "product")
        assert len(products) >= 1

        # Search for user data
        users = extractor.find_data_by_pattern(chunks, "user")
        assert len(users) >= 1

    def test_find_data_by_pattern_case_insensitive(self, extractor):
        """Test that pattern search is case insensitive"""
        html = """
        <script>self.__next_f.push([1,"{\\"Product\\": \\"Laptop\\", \\"CATEGORY\\": \\"Electronics\\"}"])</script>
        """

        chunks = extractor.parse(html)

        # Should find regardless of case
        results_lower = extractor.find_data_by_pattern(chunks, "product")
        results_upper = extractor.find_data_by_pattern(chunks, "PRODUCT")

        assert len(results_lower) >= 1
        assert len(results_upper) >= 1

    def test_find_data_by_pattern_nested(self, extractor):
        """Test finding data in nested structures"""
        html = """
        <script>self.__next_f.push([1,"{\\"data\\": {\\"products\\": [{\\"name\\": \\"Laptop\\", \\"specs\\": {\\"cpu\\": \\"Intel\\"}}]}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should find nested data
        products = extractor.find_data_by_pattern(chunks, "product")
        cpus = extractor.find_data_by_pattern(chunks, "cpu")

        assert len(products) >= 1
        assert len(cpus) >= 1

    def test_find_data_by_pattern_no_matches(self, extractor, simple_html):
        """Test pattern search with no matches"""
        chunks = extractor.parse(simple_html)

        results = extractor.find_data_by_pattern(chunks, "nonexistent_pattern")
        assert results == []

    def test_find_data_by_pattern_structure(self, extractor, ecommerce_html):
        """Test structure of pattern search results"""
        chunks = extractor.parse(ecommerce_html)
        results = extractor.find_data_by_pattern(chunks, "product")

        if results:  # If we found any results
            for result in results:
                assert "value" in result
                assert isinstance(result, dict)
                # Path might not always be present, but if it is, it should be a string
                if "path" in result:
                    assert isinstance(result["path"], str)


class TestDataAnalysis:
    """Test data analysis features"""

    def test_analyze_ecommerce_data(self, extractor, ecommerce_html):
        """Test analysis of e-commerce data"""
        chunks = extractor.parse(ecommerce_html)

        # Should be able to extract meaningful data
        assert len(chunks) >= 3

        # Look for products
        product_data = extractor.find_data_by_pattern(chunks, "products")
        assert len(product_data) >= 1

        # Look for categories
        category_data = extractor.find_data_by_pattern(chunks, "categories")
        assert len(category_data) >= 1

    def test_data_type_analysis(self, extractor, complex_html):
        """Test analysis of different data types"""
        chunks = extractor.parse(complex_html)

        # Count different data types
        type_counts = {}
        for chunk in chunks:
            for item in chunk["extracted_data"]:
                data_type = item["type"]
                type_counts[data_type] = type_counts.get(data_type, 0) + 1

        # Should find multiple data types
        assert (
            len(type_counts) >= 2
        ), f"Should find multiple data types, found: {type_counts}"

    def test_extract_structured_data(self, extractor):
        """Test extraction of structured data patterns"""
        html = """
        <script>self.__next_f.push([1,"{\\"products\\": [{\\"id\\": 1, \\"price\\": 99.99, \\"inStock\\": true}]}"])</script>
        <script>self.__next_f.push([2,"{\\"metadata\\": {\\"total\\": 100, \\"page\\": 1, \\"hasMore\\": true}}"])</script>
        """

        chunks = extractor.parse(html)

        # Extract common e-commerce patterns
        patterns = ["price", "stock", "total", "page"]
        found_patterns = {}

        for pattern in patterns:
            matches = extractor.find_data_by_pattern(chunks, pattern)
            if matches:
                found_patterns[pattern] = len(matches)

        assert (
            len(found_patterns) >= 2
        ), f"Should find multiple e-commerce patterns: {found_patterns}"


class TestErrorHandlingInSearch:
    """Test error handling in search functionality"""

    def test_search_with_error_chunks(self, extractor, malformed_html):
        """Test search functionality with error chunks present"""
        chunks = extractor.parse(malformed_html)

        # Should still be able to search despite errors
        keys = extractor.get_all_keys(chunks)
        assert isinstance(keys, dict)

        # Should find some valid data
        valid_data = extractor.find_data_by_pattern(chunks, "valid")
        assert len(valid_data) >= 1  # Should find the valid chunks

    def test_search_empty_pattern(self, extractor, simple_html):
        """Test search with empty pattern"""
        chunks = extractor.parse(simple_html)

        results = extractor.find_data_by_pattern(chunks, "")
        # Empty pattern should return empty results or handle gracefully
        assert isinstance(results, list)

    def test_search_none_pattern(self, extractor, simple_html):
        """Test search with None pattern"""
        chunks = extractor.parse(simple_html)

        # Should handle None pattern gracefully
        try:
            results = extractor.find_data_by_pattern(chunks, None)
            assert isinstance(results, list)
        except (TypeError, AttributeError):
            # It's acceptable to raise an error for None pattern
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

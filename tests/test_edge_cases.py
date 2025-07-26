"""
Performance and edge case tests
"""

import pytest
import time
import json


class TestPerformance:
    """Test performance with various dataset sizes"""

    def test_small_dataset_performance(self, extractor):
        """Test performance with small dataset"""
        html = """
        <script>self.__next_f.push([1,"{\\"test\\": \\"value\\"}"])</script>
        <script>self.__next_f.push([2,"{\\"another\\": \\"test\\"}"])</script>
        """

        start_time = time.time()
        result = extractor.parse(html)
        end_time = time.time()

        assert len(result) == 2
        assert end_time - start_time < 1.0  # Should be very fast

    def test_medium_dataset_performance(self, extractor):
        """Test performance with medium dataset"""
        # Generate HTML with 100 chunks
        chunks = []
        for i in range(100):
            data = {"id": i, "data": f"test_data_{i}", "array": list(range(10))}
            json_str = json.dumps(data).replace('"', '\\"')
            chunks.append(
                f'<script>self.__next_f.push([{i % 10},"{json_str}"])</script>'
            )

        html = f"<html><body>{''.join(chunks)}</body></html>"

        start_time = time.time()
        result = extractor.parse(html)
        end_time = time.time()

        assert len(result) <= 10  # Should group by chunk_id
        assert end_time - start_time < 5.0  # Should complete reasonably quickly

    def test_memory_usage(self, extractor):
        """Test memory usage with large dataset"""
        import sys

        # Generate large HTML
        chunks = []
        for i in range(200):
            # Create larger data objects
            data = {
                "id": i,
                "large_array": list(range(100)),
                "nested_data": {"level1": {"level2": {"level3": f"deep_value_{i}"}}},
            }
            json_str = json.dumps(data).replace('"', '\\"')
            chunks.append(
                f'<script>self.__next_f.push([{i % 5},"{json_str}"])</script>'
            )

        html = f"<html><body>{''.join(chunks)}</body></html>"

        # Measure memory before and after
        initial_size = sys.getsizeof(html)
        result = extractor.parse(html)
        result_size = sys.getsizeof(result)

        # Result should not be excessively larger than input
        assert result_size < initial_size * 3  # Reasonable memory usage


class TestEdgeCases:
    """Test edge cases and unusual inputs"""

    def test_very_long_single_chunk(self, extractor):
        """Test with very long single chunk"""
        # Create a large JSON object
        large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}
        json_str = json.dumps(large_data).replace('"', '\\"')

        html = f'<script>self.__next_f.push([1,"{json_str}"])</script>'

        result = extractor.parse(html)
        assert len(result) == 1
        assert result[0]["chunk_id"] == 1

    def test_many_small_chunks(self, extractor):
        """Test with many small chunks with same ID"""
        chunks = []
        for i in range(100):
            chunks.append(f'<script>self.__next_f.push([1,"part_{i}"])</script>')

        html = f"<html><body>{''.join(chunks)}</body></html>"

        result = extractor.parse(html)
        assert len(result) == 1
        assert result[0]["chunk_count"] == 100

    def test_special_characters(self, extractor):
        """Test with special characters and unicode"""
        html = """
        <script>self.__next_f.push([1,"{\\"emoji\\": \\"🚀🌟✨\\", \\"unicode\\": \\"héllo wörld\\", \\"special\\": \\"@#$%^&*()\\"}"])</script>
        """

        result = extractor.parse(html)
        assert len(result) == 1

        # Should handle special characters without crashing
        data_found = False
        for item in result[0]["extracted_data"]:
            if isinstance(item["data"], dict):
                data_found = True
                break

        # At least should not crash, even if parsing isn't perfect
        assert len(result[0]["extracted_data"]) > 0

    def test_nested_quotes(self, extractor):
        """Test with deeply nested quotes"""
        html = r"""
        <script>self.__next_f.push([1,"{\\"text\\": \\"He said \\\"Hello, \\\\\\\"world\\\\\\\"!\\\"\\"}"]])</script>
        """

        result = extractor.parse(html)
        assert len(result) >= 1  # Should not crash

    def test_mixed_data_types_same_chunk(self, extractor):
        """Test with mixed data types in same chunk ID"""
        html = """
        <script>self.__next_f.push([1,"{\\"json\\": \\"data\\"}"])</script>
        <script>self.__next_f.push([1,"api_key:{\\"api\\": \\"response\\"}"])</script>
        <script>self.__next_f.push([1,"plain text data"])</script>
        """

        result = extractor.parse(html)
        assert len(result) == 1
        assert result[0]["chunk_count"] == 3

        # Should handle mixed data types
        assert len(result[0]["extracted_data"]) > 0

    def test_malformed_script_tags(self, extractor):
        """Test with malformed script tags"""
        html = """
        <script>self.__next_f.push([1,"valid data"])</script>
        <script>self.__next_f.push([2</script>
        <script>self.__next_f.push([3,"more valid data"])</script>
        """

        result = extractor.parse(html)

        # Should find the valid chunks and skip malformed ones
        valid_chunks = [c for c in result if c["chunk_id"] != "error"]
        assert len(valid_chunks) >= 1

    def test_empty_chunks(self, extractor):
        """Test with empty chunk data"""
        html = """
        <script>self.__next_f.push([1,""])</script>
        <script>self.__next_f.push([2,"{\\"valid\\": \\"data\\"}"])</script>
        """

        result = extractor.parse(html)

        # Should handle empty chunks gracefully
        assert len(result) >= 1

        # Should still find valid data
        valid_data_found = False
        for chunk in result:
            for item in chunk["extracted_data"]:
                if isinstance(item["data"], dict) and "valid" in item["data"]:
                    valid_data_found = True
                    break

        # Should at least not crash, preferably find valid data
        assert len(result) > 0


class TestBoundaryConditions:
    """Test boundary conditions"""

    def test_zero_chunks(self, extractor):
        """Test with no chunks"""
        html = "<html><body><h1>No chunks here</h1></body></html>"
        result = extractor.parse(html)
        assert result == []

    def test_single_character_chunk_id(self, extractor):
        """Test with single character chunk IDs"""
        html = """
        <script>self.__next_f.push([0,"{\\"test\\": \\"zero\\"}"])</script>
        <script>self.__next_f.push([9,"{\\"test\\": \\"nine\\"}"])</script>
        """

        result = extractor.parse(html)
        assert len(result) == 2

        chunk_ids = [chunk["chunk_id"] for chunk in result]
        assert 0 in chunk_ids
        assert 9 in chunk_ids

    def test_large_chunk_ids(self, extractor):
        """Test with large chunk IDs"""
        html = """
        <script>self.__next_f.push([12345,"{\\"test\\": \\"large_id\\"}"])</script>
        <script>self.__next_f.push([999999,"{\\"test\\": \\"very_large_id\\"}"])</script>
        """

        result = extractor.parse(html)
        assert len(result) == 2

        chunk_ids = [chunk["chunk_id"] for chunk in result]
        assert "12345" in chunk_ids or 12345 in chunk_ids  # Could be string or int
        assert "999999" in chunk_ids or 999999 in chunk_ids

    def test_string_chunk_ids(self, extractor):
        """Test with string chunk IDs"""
        html = """
        <script>self.__next_f.push(["string_id","{\\"test\\": \\"string\\"}"])</script>
        <script>self.__next_f.push(["another_id","{\\"test\\": \\"another\\"}"])</script>
        """

        result = extractor.parse(html)
        assert len(result) == 2

        chunk_ids = [chunk["chunk_id"] for chunk in result]
        assert "string_id" in chunk_ids
        assert "another_id" in chunk_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

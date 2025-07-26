"""
Basic functionality tests for NextJSHydrationDataExtractor
"""

import pytest
from nextjs_hydration_parser import NextJSHydrationDataExtractor


class TestBasicFunctionality:
    """Test basic parsing functionality"""

    def test_extractor_initialization(self):
        """Test that extractor initializes correctly"""
        extractor = NextJSHydrationDataExtractor()
        assert hasattr(extractor, "script_pattern")
        assert extractor.script_pattern is not None

    def test_empty_html(self, extractor):
        """Test parsing empty HTML"""
        result = extractor.parse("")
        assert result == []

    def test_html_without_nextjs_data(self, extractor):
        """Test HTML without Next.js hydration data"""
        html = "<html><body><h1>No Next.js data here</h1></body></html>"
        result = extractor.parse(html)
        assert result == []

    def test_simple_chunk_parsing(self, extractor, simple_html):
        """Test parsing a simple chunk"""
        result = extractor.parse(simple_html)

        assert len(result) == 1
        assert result[0]["chunk_id"] == 1
        assert len(result[0]["extracted_data"]) >= 1
        assert result[0]["chunk_count"] == 1

    def test_multiple_chunks_different_ids(self, extractor):
        """Test parsing multiple chunks with different IDs"""
        html = """
        <script>self.__next_f.push([1,"{\\"test1\\": \\"value1\\"}"])</script>
        <script>self.__next_f.push([2,"{\\"test2\\": \\"value2\\"}"])</script>
        <script>self.__next_f.push([3,"{\\"test3\\": \\"value3\\"}"])</script>
        """

        result = extractor.parse(html)

        assert len(result) == 3
        chunk_ids = [chunk["chunk_id"] for chunk in result]
        assert 1 in chunk_ids
        assert 2 in chunk_ids
        assert 3 in chunk_ids

    def test_multi_chunk_same_id(self, extractor):
        """Test parsing multiple chunks with same ID (continuation)"""
        html = """
        <script>self.__next_f.push([1,"{\\"data\\": [\\"part1\\","])</script>
        <script>self.__next_f.push([1,"\\"part2\\", \\"part3\\"]}"])</script>
        """

        result = extractor.parse(html)

        assert len(result) == 1
        assert result[0]["chunk_id"] == 1
        assert result[0]["chunk_count"] == 2
        assert len(result[0]["_positions"]) == 2


class TestDataTypes:
    """Test parsing different data types"""

    def test_json_string_parsing(self, extractor):
        """Test parsing JSON string data"""
        html = '<script>self.__next_f.push([1,"{\\"key\\": \\"value\\", \\"number\\": 42}"])</script>'
        result = extractor.parse(html)

        assert len(result) == 1
        data_items = result[0]["extracted_data"]
        assert len(data_items) >= 1

        # Should find the JSON data
        json_found = False
        for item in data_items:
            if isinstance(item["data"], dict) and "key" in item["data"]:
                assert item["data"]["key"] == "value"
                assert item["data"]["number"] == 42
                json_found = True
                break
        assert json_found, "JSON data should be parsed correctly"

    def test_javascript_object_parsing(self, extractor):
        """Test parsing JavaScript object syntax"""
        html = "<script>self.__next_f.push([1,\"{key: 'value', array: [1, 2, 3]}\"])</script>"
        result = extractor.parse(html)

        assert len(result) == 1
        assert len(result[0]["extracted_data"]) >= 1

    def test_base64_colon_format(self, extractor):
        """Test parsing base64:data format"""
        html = '<script>self.__next_f.push([1,"api_key:{\\"response\\": \\"success\\"}"])</script>'
        result = extractor.parse(html)

        assert len(result) == 1
        data_items = result[0]["extracted_data"]

        # Should find colon-separated data
        colon_found = False
        for item in data_items:
            if item["type"] == "colon_separated":
                assert "identifier" in item
                colon_found = True
                break
        assert colon_found, "Colon-separated data should be detected"

    def test_escaped_strings(self, extractor):
        """Test parsing escaped string content"""
        html = r'<script>self.__next_f.push([1,"\"escaped string with \\\"quotes\\\"\""])</script>'
        result = extractor.parse(html)

        assert len(result) == 1
        assert len(result[0]["extracted_data"]) >= 1


class TestErrorHandling:
    """Test error handling and recovery"""

    def test_error_chunk_structure(self, extractor):
        """Test structure of error chunks"""
        html = '<script>self.__next_f.push([1,"{broken json}"])</script>'
        result = extractor.parse(html)

        # Should have at least one result (might be error or recovered)
        assert len(result) >= 1

        # Check if any error chunks have proper structure
        for chunk in result:
            if chunk["chunk_id"] == "error":
                assert "raw_content" in chunk
                assert "_error" in chunk
                assert "_position" in chunk

    def test_continues_after_error(self, extractor):
        """Test that parsing continues after encountering errors"""
        html = """
        <script>self.__next_f.push([1,"{\\"valid\\": \\"first\\"}"])</script>
        <script>self.__next_f.push([2,"{broken json}"])</script>
        <script>self.__next_f.push([3,"{\\"valid\\": \\"after_error\\"}"])</script>
        """

        result = extractor.parse(html)

        # Should find valid chunks before and after error
        valid_chunks = [c for c in result if c["chunk_id"] != "error"]
        assert len(valid_chunks) >= 2, "Should continue parsing after errors"


class TestPositionTracking:
    """Test position tracking functionality"""

    def test_position_tracking(self, extractor):
        """Test that positions are tracked correctly"""
        html = """start
        <script>self.__next_f.push([1,"{\\"test\\": \\"value\\"}"])</script>
        middle content
        <script>self.__next_f.push([2,"{\\"test2\\": \\"value2\\"}"])</script>
        end"""

        result = extractor.parse(html)

        assert len(result) == 2

        # Positions should be different and in ascending order
        pos1 = result[0]["_positions"][0]
        pos2 = result[1]["_positions"][0]

        assert pos1 != pos2
        assert pos1 < pos2  # First chunk should appear before second

    def test_multi_chunk_positions(self, extractor):
        """Test position tracking for multi-chunk data"""
        html = """
        <script>self.__next_f.push([1,"first part"])</script>
        some content
        <script>self.__next_f.push([1,"second part"])</script>
        """

        result = extractor.parse(html)

        assert len(result) == 1
        assert result[0]["chunk_count"] == 2
        assert len(result[0]["_positions"]) == 2
        assert result[0]["_positions"][0] < result[0]["_positions"][1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

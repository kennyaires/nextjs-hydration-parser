"""
Test configuration and fixtures for Next.js Hydration Parser tests
"""

import pytest


# Sample HTML content for testing
SIMPLE_HTML = """
<html>
<body>
    <script>self.__next_f.push([1,"{\\"test\\": \\"value\\"}"])</script>
</body>
</html>
"""

COMPLEX_HTML = """
<html>
<head><title>Test</title></head>
<body>
    <div id="__next">Content</div>
    
    <!-- Simple JSON -->
    <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Laptop\\"}]}"])</script>
    
    <!-- Multi-chunk data -->
    <script>self.__next_f.push([2,"{\\"users\\":[{\\"id\\":1,"])</script>
    <script>self.__next_f.push([2,"\\"name\\":\\"John\\"}]}"])</script>
    
    <!-- Base64 + JSON -->
    <script>self.__next_f.push([3,"api_key:{\\"response\\":{\\"status\\":\\"ok\\"}}"])</script>
    
    <!-- JavaScript object -->
    <script>self.__next_f.push([4,"{key: 'value', array: [1, 2, 3]}"])</script>
    
    <!-- Escaped content -->
    <script>self.__next_f.push([5,"\\"escaped string with \\\"quotes\\\"\\""])</script>
</body>
</html>
"""

MALFORMED_HTML = """
<html>
<body>
    <!-- Valid chunk -->
    <script>self.__next_f.push([1,"{\\"valid\\": \\"data\\"}"])</script>
    
    <!-- Invalid JSON -->
    <script>self.__next_f.push([2,"{broken: json}"])</script>
    
    <!-- Incomplete data -->
    <script>self.__next_f.push([3,"{\\"incomplete\\":"])</script>
    
    <!-- Another valid chunk -->
    <script>self.__next_f.push([4,"{\\"another\\": \\"valid\\"}"])</script>
</body>
</html>
"""

ECOMMERCE_HTML = """
<html>
<body>
    <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Gaming Laptop\\",\\"price\\":1299.99,\\"inStock\\":true,\\"category\\":\\"electronics\\"}]}"])</script>
    <script>self.__next_f.push([2,"{\\"categories\\":[{\\"id\\":1,\\"name\\":\\"Electronics\\"},{\\"id\\":2,\\"name\\":\\"Books\\"}]}"])</script>
    <script>self.__next_f.push([3,"{\\"user\\":{\\"id\\":123,\\"cart\\":{\\"items\\":[{\\"productId\\":1,\\"quantity\\":2}],\\"total\\":2599.98}}}"])</script>
</body>
</html>
"""


@pytest.fixture
def simple_html():
    """Simple HTML with one chunk"""
    return SIMPLE_HTML


@pytest.fixture
def complex_html():
    """Complex HTML with various data types"""
    return COMPLEX_HTML


@pytest.fixture
def malformed_html():
    """HTML with some malformed data"""
    return MALFORMED_HTML


@pytest.fixture
def ecommerce_html():
    """E-commerce style HTML"""
    return ECOMMERCE_HTML


@pytest.fixture
def extractor():
    """Create a fresh extractor instance"""
    from nextjs_hydration_parser import NextJSHydrationDataExtractor

    return NextJSHydrationDataExtractor()

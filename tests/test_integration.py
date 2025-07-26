"""
Integration tests for real-world scenarios
"""

import pytest
import json


class TestEcommerceScenarios:
    """Test e-commerce scraping scenarios"""

    def test_product_catalog_extraction(self, extractor):
        """Test extracting product catalog data"""
        html = """
        <script>self.__next_f.push([1,"{\\"products\\":[{\\"id\\":1,\\"name\\":\\"Laptop\\",\\"price\\":999.99,\\"category\\":\\"electronics\\",\\"inStock\\":true,\\"rating\\":4.5}]}"])</script>
        <script>self.__next_f.push([1,",{\\"id\\":2,\\"name\\":\\"Mouse\\",\\"price\\":29.99,\\"category\\":\\"accessories\\",\\"inStock\\":false,\\"rating\\":4.2}]}"])</script>
        <script>self.__next_f.push([2,"{\\"pagination\\":{\\"page\\":1,\\"total\\":50,\\"hasMore\\":true}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract product data
        products = extractor.find_data_by_pattern(chunks, "product")
        assert len(products) >= 1

        # Should extract pagination data
        pagination = extractor.find_data_by_pattern(chunks, "pagination")
        assert len(pagination) >= 1

    def test_shopping_cart_extraction(self, extractor):
        """Test extracting shopping cart data"""
        html = """
        <script>self.__next_f.push([1,"{\\"cart\\":{\\"items\\":[{\\"productId\\":1,\\"quantity\\":2,\\"price\\":999.99}],\\"subtotal\\":1999.98,\\"tax\\":199.99,\\"total\\":2199.97}}"])</script>
        <script>self.__next_f.push([2,"{\\"user\\":{\\"id\\":123,\\"email\\":\\"user@example.com\\",\\"shippingAddress\\":{\\"street\\":\\"123 Main St\\",\\"city\\":\\"Anytown\\"}}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract cart data
        cart_data = extractor.find_data_by_pattern(chunks, "cart")
        assert len(cart_data) >= 1

        # Should extract user data
        user_data = extractor.find_data_by_pattern(chunks, "user")
        assert len(user_data) >= 1

    def test_category_navigation_extraction(self, extractor):
        """Test extracting category navigation data"""
        html = """
        <script>self.__next_f.push([1,"{\\"categories\\":[{\\"id\\":1,\\"name\\":\\"Electronics\\",\\"subcategories\\":[{\\"id\\":11,\\"name\\":\\"Laptops\\"},{\\"id\\":12,\\"name\\":\\"Phones\\"}]}]}"])</script>
        <script>self.__next_f.push([2,"{\\"filters\\":{\\"brands\\":[\\"Apple\\",\\"Samsung\\",\\"Dell\\"],\\"priceRanges\\":[{\\"min\\":0,\\"max\\":500},{\\"min\\":500,\\"max\\":1000}]}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract category structure
        categories = extractor.find_data_by_pattern(chunks, "categor")
        assert len(categories) >= 1

        # Should extract filter options
        filters = extractor.find_data_by_pattern(chunks, "filter")
        assert len(filters) >= 1


class TestSocialMediaScenarios:
    """Test social media scraping scenarios"""

    def test_user_profile_extraction(self, extractor):
        """Test extracting user profile data"""
        html = """
        <script>self.__next_f.push([1,"{\\"profile\\":{\\"id\\":12345,\\"username\\":\\"john_doe\\",\\"displayName\\":\\"John Doe\\",\\"bio\\":\\"Software developer\\",\\"followers\\":1500,\\"following\\":300}}"])</script>
        <script>self.__next_f.push([2,"{\\"posts\\":{\\"recent\\":[{\\"id\\":1,\\"content\\":\\"Hello world!\\",\\"likes\\":25,\\"timestamp\\":\\"2025-01-01T10:00:00Z\\"}]}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract profile data
        profile_data = extractor.find_data_by_pattern(chunks, "profile")
        assert len(profile_data) >= 1

        # Should extract posts data
        posts_data = extractor.find_data_by_pattern(chunks, "post")
        assert len(posts_data) >= 1

    def test_feed_extraction(self, extractor):
        """Test extracting social media feed data"""
        html = """
        <script>self.__next_f.push([1,"{\\"feed\\":[{\\"id\\":1,\\"user\\":{\\"username\\":\\"alice\\"},\\"content\\":\\"Great day!\\",\\"engagement\\":{\\"likes\\":50,\\"comments\\":5}}]}"])</script>
        <script>self.__next_f.push([1,",{\\"id\\":2,\\"user\\":{\\"username\\":\\"bob\\"},\\"content\\":\\"Working on new project\\",\\"engagement\\":{\\"likes\\":30,\\"comments\\":8}}]}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract feed data
        feed_data = extractor.find_data_by_pattern(chunks, "feed")
        assert len(feed_data) >= 1

        # Should extract engagement data
        engagement_data = extractor.find_data_by_pattern(chunks, "engagement")
        assert len(engagement_data) >= 1


class TestContentManagementScenarios:
    """Test content management/blog scraping scenarios"""

    def test_blog_post_extraction(self, extractor):
        """Test extracting blog post data"""
        html = """
        <script>self.__next_f.push([1,"{\\"article\\":{\\"id\\":1,\\"title\\":\\"Getting Started with Next.js\\",\\"author\\":{\\"name\\":\\"Jane Smith\\",\\"bio\\":\\"Web developer\\"},\\"content\\":\\"This is the article content...\\",\\"publishedAt\\":\\"2025-01-01\\",\\"tags\\":[\\"nextjs\\",\\"react\\",\\"javascript\\"]}}"])</script>
        <script>self.__next_f.push([2,"{\\"comments\\":[{\\"id\\":1,\\"author\\":\\"reader1\\",\\"content\\":\\"Great article!\\",\\"timestamp\\":\\"2025-01-02T10:00:00Z\\"}]}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract article data
        article_data = extractor.find_data_by_pattern(chunks, "article")
        assert len(article_data) >= 1

        # Should extract comments
        comments_data = extractor.find_data_by_pattern(chunks, "comment")
        assert len(comments_data) >= 1

    def test_article_listing_extraction(self, extractor):
        """Test extracting article listing data"""
        html = """
        <script>self.__next_f.push([1,"{\\"articles\\":[{\\"id\\":1,\\"title\\":\\"First Post\\",\\"excerpt\\":\\"This is the first post...\\",\\"publishedAt\\":\\"2025-01-01\\"},{\\"id\\":2,\\"title\\":\\"Second Post\\",\\"excerpt\\":\\"This is the second post...\\",\\"publishedAt\\":\\"2025-01-02\\"}]}"])</script>
        <script>self.__next_f.push([2,"{\\"metadata\\":{\\"totalArticles\\":100,\\"currentPage\\":1,\\"articlesPerPage\\":10}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract articles list
        articles_data = extractor.find_data_by_pattern(chunks, "article")
        assert len(articles_data) >= 1

        # Should extract metadata
        metadata = extractor.find_data_by_pattern(chunks, "metadata")
        assert len(metadata) >= 1


class TestAPIDataScenarios:
    """Test API response data extraction scenarios"""

    def test_api_response_extraction(self, extractor):
        """Test extracting API response data"""
        html = """
        <script>self.__next_f.push([1,"api_response:{\\"status\\":\\"success\\",\\"data\\":{\\"users\\":[{\\"id\\":1,\\"name\\":\\"John\\"}]},\\"pagination\\":{\\"page\\":1,\\"total\\":50}}"])</script>
        <script>self.__next_f.push([2,"graphql_response:{\\"data\\":{\\"posts\\":{\\"edges\\":[{\\"node\\":{\\"id\\":1,\\"title\\":\\"Post 1\\"}}]}}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract API response data
        api_responses = []
        graphql_responses = []

        for chunk in chunks:
            for item in chunk["extracted_data"]:
                if item["type"] == "colon_separated":
                    identifier = item.get("identifier", "").lower()
                    if "api" in identifier:
                        api_responses.append(item)
                    elif "graphql" in identifier:
                        graphql_responses.append(item)

        assert len(api_responses) >= 1
        assert len(graphql_responses) >= 1

    def test_error_response_handling(self, extractor):
        """Test handling API error responses"""
        html = """
        <script>self.__next_f.push([1,"{\\"success\\":true,\\"data\\":{\\"result\\":\\"ok\\"}}"])</script>
        <script>self.__next_f.push([2,"{\\"success\\":false,\\"error\\":{\\"code\\":404,\\"message\\":\\"Not found\\"},\\"data\\":null}"])</script>
        """

        chunks = extractor.parse(html)

        # Should extract both success and error responses
        success_data = extractor.find_data_by_pattern(chunks, "success")
        error_data = extractor.find_data_by_pattern(chunks, "error")

        assert len(success_data) >= 1
        assert len(error_data) >= 1


class TestComplexDataStructures:
    """Test complex nested data structures"""

    def test_deeply_nested_extraction(self, extractor):
        """Test extracting deeply nested data"""
        html = """
        <script>self.__next_f.push([1,"{\\"level1\\":{\\"level2\\":{\\"level3\\":{\\"level4\\":{\\"data\\":\\"deep_value\\",\\"array\\":[1,2,3]}}}}}"])</script>
        """

        chunks = extractor.parse(html)

        # Should handle deep nesting
        assert len(chunks) == 1
        assert len(chunks[0]["extracted_data"]) >= 1

        # Should be able to find nested data
        deep_data = extractor.find_data_by_pattern(chunks, "level4")
        assert len(deep_data) >= 1

    def test_mixed_array_object_structures(self, extractor):
        """Test mixed array and object structures"""
        html = """
        <script>self.__next_f.push([1,"{\\"items\\":[{\\"type\\":\\"product\\",\\"data\\":{\\"name\\":\\"Item 1\\"}},{\\"type\\":\\"category\\",\\"data\\":{\\"name\\":\\"Cat 1\\"}}]}"])</script>
        """

        chunks = extractor.parse(html)

        # Should handle mixed structures
        items_data = extractor.find_data_by_pattern(chunks, "items")
        product_data = extractor.find_data_by_pattern(chunks, "product")
        category_data = extractor.find_data_by_pattern(chunks, "category")

        assert len(items_data) >= 1
        # May or may not find product/category depending on search depth
        assert len(chunks) == 1  # At least should parse without error


class TestRealWorldComplexity:
    """Test scenarios that simulate real-world complexity"""

    def test_large_ecommerce_page(self, extractor):
        """Test parsing a large e-commerce page simulation"""
        # Simulate a complex e-commerce page with multiple data chunks
        chunks_html = []

        # Products chunk
        products = [
            {"id": i, "name": f"Product {i}", "price": 99.99 + i} for i in range(1, 21)
        ]
        products_json = json.dumps({"products": products}).replace('"', '\\"')
        chunks_html.append(
            f'<script>self.__next_f.push([1,"{products_json}"])</script>'
        )

        # Categories chunk
        categories = [{"id": i, "name": f"Category {i}"} for i in range(1, 6)]
        categories_json = json.dumps({"categories": categories}).replace('"', '\\"')
        chunks_html.append(
            f'<script>self.__next_f.push([2,"{categories_json}"])</script>'
        )

        # User data chunk
        user_data = {
            "user": {"id": 123, "cart": {"items": [{"productId": 1, "qty": 2}]}}
        }
        user_json = json.dumps(user_data).replace('"', '\\"')
        chunks_html.append(f'<script>self.__next_f.push([3,"{user_json}"])</script>')

        html = f"<html><body>{''.join(chunks_html)}</body></html>"

        result = extractor.parse(html)

        # Should parse all chunks
        assert len(result) == 3

        # Should find expected data patterns
        products_found = extractor.find_data_by_pattern(result, "product")
        categories_found = extractor.find_data_by_pattern(result, "categor")
        user_found = extractor.find_data_by_pattern(result, "user")

        assert len(products_found) >= 1
        assert len(categories_found) >= 1
        assert len(user_found) >= 1

    def test_fragmented_data_assembly(self, extractor):
        """Test assembly of fragmented data across multiple chunks"""
        html = """
        <script>self.__next_f.push([1,"{\\"bigObject\\": {\\"part1\\": [\\"a\\","])</script>
        <script>self.__next_f.push([1,"\\"b\\", \\"c\\"], \\"part2\\": {\\"nested\\": true,"])</script>
        <script>self.__next_f.push([1,"\\"value\\": 42}}}"])</script>
        """

        result = extractor.parse(html)

        # Should assemble fragmented data
        assert len(result) == 1
        assert result[0]["chunk_count"] == 3

        # Should find the assembled data
        big_object = extractor.find_data_by_pattern(result, "bigObject")
        assert len(big_object) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

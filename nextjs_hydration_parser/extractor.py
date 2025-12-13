import re
import json
import logging
from typing import Dict, List, Any, Optional
import chompjs


class NextJSHydrationDataExtractor:
    """
    A class for extracting and parsing Next.js hydration data from HTML content.

    This class provides methods to parse self.__next_f.push calls and extract
    structured data from Next.js hydration scripts.
    """

    def __init__(self):
        """
        Initialize the extractor.
        """
        self.script_pattern = r"self\.__next_f\.push\(\[(.*?)\]\)"
        self.logger = logging.getLogger(__name__)
        self._lightweight_cache = {}

    def parse(
        self,
        html_content: str,
        lightweight: bool = False,
        target_patterns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse Next.js/Nuxt.js hydration data from script tags containing self.__next_f.push calls.
        Returns a list of parsed data chunks, preserving all available information.

        Args:
            html_content (str): Raw HTML content containing script tags
            lightweight (bool): If True, only extract chunks containing target patterns (much faster)
            target_patterns (Optional[List[str]]): List of strings to search for in lightweight mode.
                                                    If None in lightweight mode, only parses chunk structure without deep extraction.

        Returns:
            List[Dict[str, Any]]: List of parsed data chunks
        """

        # Find all script matches with their positions
        raw_chunks = []
        for match in re.finditer(self.script_pattern, html_content, re.DOTALL):
            chunk_content = match.group(1)
            position = match.start()

            # In lightweight mode with patterns, filter early
            if lightweight and target_patterns:
                # Quick check if any pattern exists in the chunk
                if not any(pattern in chunk_content for pattern in target_patterns):
                    continue

            try:
                # Parse the chunk content more carefully
                parsed_chunk = self._parse_single_chunk(chunk_content)
                if parsed_chunk:
                    parsed_chunk["_position"] = position
                    raw_chunks.append(parsed_chunk)
            except Exception as e:
                self.logger.debug(f"Error parsing chunk at position {position}: {e}")
                # Still add raw content for debugging
                raw_chunks.append(
                    {
                        "chunk_id": "error",
                        "raw_content": chunk_content,
                        "_position": position,
                        "_error": str(e),
                    }
                )

        # Sort by position to maintain order
        raw_chunks.sort(key=lambda x: x["_position"])

        # Group chunks and handle continuations
        processed_chunks = self._process_chunks(
            raw_chunks, lightweight=lightweight, target_patterns=target_patterns
        )

        return processed_chunks

    def _parse_single_chunk(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single chunk content from self.__next_f.push([chunk_id, data]).

        Args:
            content (str): The content inside the brackets

        Returns:
            Dict[str, Any]: Parsed chunk or None if parsing fails
        """

        content = content.strip()

        # Try multiple parsing strategies

        # Strategy 1: Use chompjs to parse as array
        try:
            parsed_array = chompjs.parse_js_object(f"[{content}]")
            if len(parsed_array) >= 2:
                chunk_id = parsed_array[0]
                chunk_data = str(parsed_array[1])
                return {
                    "chunk_id": chunk_id,
                    "raw_data": chunk_data,
                    "parsed_data": None,  # Will be filled later
                }
        except:
            pass

        # Strategy 2: Manual parsing - find first comma outside quotes
        comma_pos = self._find_separator_comma(content)
        if comma_pos != -1:
            chunk_id_part = content[:comma_pos].strip()
            data_part = content[comma_pos + 1 :].strip()

            # Parse chunk_id
            try:
                chunk_id = chompjs.parse_js_object(chunk_id_part)
            except:
                chunk_id = chunk_id_part.strip("\"'")

            # Clean data part (remove surrounding quotes and unescape)
            if data_part.startswith('"') and data_part.endswith('"'):
                data_part = data_part[1:-1]
                data_part = data_part.replace('\\"', '"').replace("\\\\", "\\")

            return {"chunk_id": chunk_id, "raw_data": data_part, "parsed_data": None}

        # Strategy 3: Treat entire content as data with unknown ID
        return {"chunk_id": "unknown", "raw_data": content, "parsed_data": None}

    def _process_chunks(
        self,
        raw_chunks: List[Dict[str, Any]],
        lightweight: bool = False,
        target_patterns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process raw chunks, combining continuations and extracting JSON data.

        Args:
            raw_chunks (List[Dict]): List of raw parsed chunks
            lightweight (bool): If True, skip deep extraction for non-matching chunks
            target_patterns (Optional[List[str]]): Patterns to filter by in lightweight mode

        Returns:
            List[Dict[str, Any]]: List of processed data chunks
        """

        # Group chunks by ID first
        chunks_by_id = {}
        for chunk in raw_chunks:
            chunk_id = chunk["chunk_id"]
            if chunk_id not in chunks_by_id:
                chunks_by_id[chunk_id] = []
            chunks_by_id[chunk_id].append(chunk)

        # Process each group
        result = []

        for chunk_id, chunk_list in chunks_by_id.items():
            # Sort by position to maintain order
            chunk_list.sort(key=lambda x: x["_position"])

            # Combine all data for this chunk_id
            combined_data = "".join([chunk["raw_data"] for chunk in chunk_list])

            # In lightweight mode, do minimal processing unless patterns match
            if lightweight and target_patterns:
                # Check if this chunk contains any target patterns
                if not any(pattern in combined_data for pattern in target_patterns):
                    # Skip detailed extraction for non-matching chunks
                    processed_chunk = {
                        "chunk_id": chunk_id,
                        "extracted_data": [],
                        "chunk_count": len(chunk_list),
                        "_skipped": True,
                        "_positions": [chunk["_position"] for chunk in chunk_list],
                    }
                    result.append(processed_chunk)
                    continue

            # Try to extract structured data
            extracted_items = self._extract_all_data_structures(combined_data)

            processed_chunk = {
                "chunk_id": chunk_id,
                "extracted_data": extracted_items,
                "chunk_count": len(chunk_list),
                "_positions": [chunk["_position"] for chunk in chunk_list],
            }

            result.append(processed_chunk)

        return result

    def _extract_all_data_structures(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all possible data structures from a text string.
        Handles various patterns like base64:json, plain json, etc.

        Args:
            text (str): Text to parse

        Returns:
            List[Dict[str, Any]]: List of extracted data structures
        """

        extracted = []

        if not text or not text.strip():
            return extracted

        # Pattern 1: Look for base64_id:json_content patterns
        colon_matches = re.finditer(r"([^:]*):(\{.*)", text)
        for match in colon_matches:
            identifier = match.group(1).strip()
            json_part = match.group(2)

            # Try to extract complete JSON from this position
            complete_json = self._extract_complete_json(json_part)
            if complete_json:
                parsed_json = self._parse_js_object(complete_json)
                if parsed_json is not None:
                    extracted.append(
                        {
                            "type": "colon_separated",
                            "identifier": identifier,
                            "data": parsed_json,
                            "raw_json": complete_json,
                        }
                    )

        # Pattern 2: Look for standalone JSON objects/arrays
        json_starts = []
        for match in re.finditer(r"[\{\[]", text):
            json_starts.append(match.start())

        for start_pos in json_starts:
            substring = text[start_pos:]
            complete_json = self._extract_complete_json(substring)

            # check if complete_json was not extracted already
            if complete_json and any(
                complete_json in item.get("raw_json") for item in extracted
            ):
                continue
            if complete_json and len(complete_json) > 10:  # Skip very small objects
                parsed_json = self._parse_js_object(complete_json)
                if parsed_json is not None:
                    # Avoid duplicates
                    if not any(
                        item.get("raw_json") == complete_json for item in extracted
                    ):
                        extracted.append(
                            {
                                "type": "standalone_json",
                                "data": parsed_json,
                                "raw_json": complete_json,
                                "start_position": start_pos,
                            }
                        )

        # Pattern 3: Try parsing the entire text as JSON
        if not extracted:
            parsed_whole = self._parse_js_object(text)
            if parsed_whole is not None:
                extracted.append(
                    {"type": "whole_text", "data": parsed_whole, "raw_json": text}
                )

        # Remove raw_json from the final output
        for item in extracted:
            if "raw_json" in item:
                del item["raw_json"]

        return extracted

    def _parse_js_object(self, text: str) -> Any:
        """
        Parse JavaScript object/JSON from text using multiple strategies.

        Args:
            text (str): String containing JavaScript object or JSON

        Returns:
            Any: Parsed object or None if parsing fails
        """

        if not text or not text.strip():
            return None

        text = text.strip()

        # Strategy 1: Try chompjs (best for JS objects)
        try:
            return chompjs.parse_js_object(text)
        except:
            pass

        # Strategy 2: Try standard JSON
        try:
            return json.loads(text)
        except:
            pass

        # Strategy 3: Clean up and try again
        try:
            cleaned = self._clean_js_object(text)
            return chompjs.parse_js_object(cleaned)
        except:
            pass

        try:
            cleaned = self._clean_js_object(text)
            return json.loads(cleaned)
        except:
            pass

        return None

    def _clean_js_object(self, text: str) -> str:
        """
        Clean up common JavaScript object issues for JSON parsing.

        Args:
            text (str): Raw JavaScript object string

        Returns:
            str: Cleaned string
        """

        # Remove trailing commas before closing braces/brackets
        text = re.sub(r",(\s*[}\]])", r"\1", text)

        # Remove JavaScript comments
        text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

        return text.strip()

    def _extract_complete_json(self, text: str) -> Optional[str]:
        """
        Extract a complete JSON object or array from the beginning of a string.

        Args:
            text (str): String starting with JSON

        Returns:
            str: Complete JSON string or None if not found
        """

        if not text:
            return None

        # Find the actual start of JSON (skip whitespace)
        start_idx = 0
        while start_idx < len(text) and text[start_idx].isspace():
            start_idx += 1

        if start_idx >= len(text):
            return None

        first_char = text[start_idx]
        if first_char == "{":
            open_char, close_char = "{", "}"
        elif first_char == "[":
            open_char, close_char = "[", "]"
        else:
            return None

        count = 0
        in_string = False
        escape_next = False

        for i in range(start_idx, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == "\\" and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == open_char:
                    count += 1
                elif char == close_char:
                    count -= 1

                    if count == 0:
                        return text[start_idx : i + 1]

        return None

    def _find_separator_comma(self, text: str) -> int:
        """
        Find the comma that separates chunk_id from chunk_data.

        Args:
            text (str): Text to search

        Returns:
            int: Position of separator comma, or -1 if not found
        """

        in_quotes = False
        quote_char = None
        escape_next = False
        paren_count = 0
        bracket_count = 0
        brace_count = 0

        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char in "\"'":
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                continue

            if not in_quotes:
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                elif char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                elif char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                elif (
                    char == ","
                    and paren_count == 0
                    and bracket_count == 0
                    and brace_count == 0
                ):
                    return i

        return -1

    def get_all_keys(
        self, parsed_chunks: List[Dict[str, Any]], max_depth: int = 3
    ) -> Dict[str, int]:
        """
        Get all unique keys from the parsed chunks.

        Args:
            parsed_chunks (List[Dict]): Output from parse method
            max_depth (int): Maximum depth to traverse when collecting keys

        Returns:
            Dict[str, int]: Dictionary of keys and their occurrence count
        """

        key_counts = {}

        def collect_keys(obj, depth=0):
            if depth > max_depth:
                return

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if not key.startswith("_"):  # Skip internal keys
                        key_counts[key] = key_counts.get(key, 0) + 1
                        collect_keys(value, depth + 1)

            elif isinstance(obj, list):
                for item in obj:
                    collect_keys(item, depth + 1)

        for chunk in parsed_chunks:
            if "extracted_data" in chunk:
                for extracted_item in chunk["extracted_data"]:
                    if "data" in extracted_item:
                        collect_keys(extracted_item["data"])

        return dict(sorted(key_counts.items(), key=lambda x: x[1], reverse=True))

    def find_data_by_pattern(
        self, parsed_chunks: List[Dict[str, Any]], pattern: str
    ) -> List[Any]:
        """
        Find data that matches a specific pattern.

        Args:
            parsed_chunks (List[Dict]): Output from parse method
            pattern (str): Key pattern to search for

        Returns:
            List[Any]: List of matching data items
        """

        results = []

        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if pattern.lower() in key.lower():
                        results.append(
                            {"path": current_path, "key": key, "value": value}
                        )

                    search_recursive(value, current_path)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_recursive(item, current_path)

        for chunk in parsed_chunks:
            if "extracted_data" in chunk:
                for extracted_item in chunk["extracted_data"]:
                    if "data" in extracted_item:
                        search_recursive(
                            extracted_item["data"], f"chunk_{chunk['chunk_id']}"
                        )

        return results

    def parse_and_find(self, html_content: str, patterns: List[str]) -> List[Any]:
        """
        Convenience method: Parse HTML in lightweight mode and find data matching patterns.
        This is much faster than full parsing when you know what you're looking for.

        Args:
            html_content (str): Raw HTML content
            patterns (List[str]): List of key patterns to search for (e.g., ["listingsConnection", "product"])

        Returns:
            List[Any]: List of matching data items

        Example:
            >>> extractor = NextJSHydrationDataExtractor()
            >>> results = extractor.parse_and_find(html, ["listingsConnection"])
        """
        # Parse in lightweight mode with target patterns
        parsed = self.parse(html_content, lightweight=True, target_patterns=patterns)

        # Find all matching data
        all_results = []
        for pattern in patterns:
            results = self.find_data_by_pattern(parsed, pattern)
            all_results.extend(results)

        return all_results

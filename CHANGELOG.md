# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-12-13

### Added
- **Lightweight parsing mode** for dramatically improved performance on large pages (10-15x faster)
  - New `lightweight` parameter in `parse()` method
  - New `target_patterns` parameter to filter chunks by content
  - New `parse_and_find()` convenience method for quick pattern-based extraction
- Performance optimizations for large HTML files with hundreds of chunks
- Examples demonstrating lightweight mode usage (`lightweight_mode_demo.py`)

### Changed
- Updated documentation with lightweight mode examples and performance comparisons
- Enhanced README with real-world use cases and performance metrics

### Performance
- Parsing large e-commerce pages reduced from ~12s to <1s when using lightweight mode
- Memory usage reduced when parsing with target patterns

## [0.3.0] - 2025-12-10

### Added
- Initial public release
- Core parsing functionality for Next.js hydration data
- Support for multiple data formats (JSON, base64, escaped content)
- Chunk reassembly for fragmented data
- Pattern matching with `find_data_by_pattern()`
- Key extraction with `get_all_keys()`

### Features
- Robust error handling for malformed chunks
- Multiple parsing strategies for different encoding formats
- Comprehensive examples and documentation

## [Unreleased]

### Planned
- Streaming parser for extremely large files
- Caching layer for repeated parsing
- Additional output formats (pandas DataFrame, CSV)
- CLI tool for quick data extraction

# Contributing to Next.js Hydration Parser

Thank you for your interest in contributing to Next.js Hydration Parser! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/kennyaires/nextjs-hydration-parser.git
   cd nextjs-hydration-parser
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. **Make your changes** and commit them
6. **Push to your fork** and create a Pull Request

## 🧪 Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/kennyaires/nextjs-hydration-parser.git
cd nextjs-hydration-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .[dev]
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=nextjs_hydration_parser --cov-report=html

# Run specific test file
pytest tests/test_basic.py -v

# Run tests for specific functionality
pytest tests/ -k "test_parsing" -v
```

### Code Quality
```bash
# Format code
black nextjs_hydration_parser/ tests/ examples/

# Check formatting
black --check nextjs_hydration_parser/ tests/ examples/

# Sort imports
isort nextjs_hydration_parser/ tests/ examples/
```

### Running Examples
```bash
# Run all examples
python run_examples.py

# Run specific example
python examples/basic_usage.py
```

## 📝 Contribution Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 88)
- Use type hints where appropriate
- Write descriptive docstrings for all public functions and classes

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:
```
feat(parser): add support for nested JSON objects
fix(extractor): handle malformed script tags gracefully
docs(readme): update installation instructions
test(integration): add e-commerce scraping tests
```

### Pull Request Process

1. **Create descriptive PR title** following conventional commit format
2. **Fill out PR template** with detailed description
3. **Ensure all tests pass** locally before submitting
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Request review** from maintainers

### Testing Requirements
- All new features must include tests
- Maintain test coverage above 80%
- Add integration tests for complex features
- Include edge case testing

## 🐛 Reporting Bugs

1. **Search existing issues** first
2. **Use the bug report template**
3. **Include minimal reproduction case**
4. **Provide system information** (Python version, OS, etc.)
5. **Include error logs** and stack traces

## 💡 Suggesting Features

1. **Check existing feature requests** first
2. **Use the feature request template**
3. **Provide clear use case** and rationale
4. **Include example usage** if possible
5. **Consider implementation complexity**

## 🔍 Areas for Contribution

### High Priority
- **Performance optimization** for large HTML files
- **Enhanced error handling** and recovery
- **Support for additional data formats**
- **Better documentation** and examples

### Medium Priority
- **Command-line interface** for the tool
- **Integration with popular scraping frameworks**
- **Additional parsing strategies**
- **Improved debugging output**

### Low Priority
- **Web UI** for testing the parser
- **Browser extension** for live parsing
- **Performance benchmarking** tools

## 🏗️ Project Structure

```
nextjs_hydration_parser/
├── nextjs_hydration_parser/     # Main package
│   ├── __init__.py             # Package initialization
│   └── extractor.py            # Core extraction logic
├── tests/                      # Test suite
│   ├── conftest.py            # Test configuration
│   ├── test_basic.py          # Basic functionality tests
│   ├── test_search.py         # Search functionality tests
│   ├── test_edge_cases.py     # Edge cases and performance
│   └── test_integration.py    # Integration tests
├── examples/                   # Usage examples
│   ├── basic_usage.py         # Basic usage example
│   ├── ecommerce_scraping.py  # E-commerce example
│   ├── real_world_scraping.py # Real-world scraping
│   ├── advanced_features.py   # Advanced features
│   └── sample_html_analysis.py # Sample file analysis
├── .github/                    # GitHub configuration
│   ├── workflows/             # CI/CD workflows
│   └── ISSUE_TEMPLATE/        # Issue templates
├── README.md                   # Project documentation
├── setup.py                    # Package setup
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
└── LICENSE                     # MIT License
```

## 🔒 Security

- **Never commit sensitive data** (API keys, credentials, etc.)
- **Follow responsible disclosure** for security vulnerabilities
- **Report security issues** privately to maintainers
- **Respect website terms of service** in examples and tests

## 📚 Documentation

- **Update README** for user-facing changes
- **Add docstrings** to all public functions
- **Include examples** for new features
- **Update changelog** for releases

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 🎉 Recognition

Contributors will be recognized in:
- README contributors section
- Release notes
- GitHub contributor graph

Thank you for contributing to Next.js Hydration Parser! 🚀

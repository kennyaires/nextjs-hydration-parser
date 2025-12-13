#!/usr/bin/env python3
"""Setup script for nextjs-hydration-parser package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nextjs-hydration-parser",
    version="0.4.0",
    author="Kenny Aires",
    description="A Python library for extracting and parsing Next.js hydration data from HTML content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kennyaires/nextjs-hydration-parser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.7",
    install_requires=[
        "chompjs>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "mypy>=0.800",
        ],
    },
    keywords="nextjs, hydration, html, parser, web-scraping, javascript",
    project_urls={
        "Bug Reports": "https://github.com/kennyaires/nextjs-hydration-parser/issues",
        "Source": "https://github.com/kennyaires/nextjs-hydration-parser",
        "Documentation": "https://github.com/kennyaires/nextjs-hydration-parser#readme",
    },
)

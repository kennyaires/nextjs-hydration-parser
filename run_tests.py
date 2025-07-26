#!/usr/bin/env python3
"""
Test runner script for Next.js Hydration Parser

This script runs all tests and provides a summary of results.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run all tests and return results"""

    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"

    print("Next.js Hydration Parser - Test Runner")
    print("=" * 50)

    # Check if pytest is available
    try:
        import pytest

        print(f"Using pytest from: {pytest.__file__}")
    except ImportError:
        print("ERROR: pytest not found. Please install with:")
        print("pip install pytest")
        return False

    # Run different test categories
    test_files = [
        ("Basic Functionality", "test_basic.py"),
        ("Search & Analysis", "test_search.py"),
        ("Edge Cases & Performance", "test_edge_cases.py"),
        ("Integration Tests", "test_integration.py"),
    ]

    results = {}
    overall_success = True

    for category, test_file in test_files:
        print(f"\n--- Running {category} ---")
        test_path = tests_dir / test_file

        if not test_path.exists():
            print(f"WARNING: Test file not found: {test_path}")
            results[category] = "MISSING"
            continue

        try:
            # Run pytest for this specific file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            if result.returncode == 0:
                print(f"✓ {category}: PASSED")
                results[category] = "PASSED"
            else:
                print(f"✗ {category}: FAILED")
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                print("STDERR:", result.stderr[-500:])
                results[category] = "FAILED"
                overall_success = False

        except Exception as e:
            print(f"✗ {category}: ERROR - {e}")
            results[category] = f"ERROR: {e}"
            overall_success = False

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    for category, result in results.items():
        status_symbol = "✓" if result == "PASSED" else "✗"
        print(f"{status_symbol} {category}: {result}")

    if overall_success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed. Check output above for details.")
        return False


def run_coverage():
    """Run tests with coverage report"""

    print("\n" + "=" * 50)
    print("RUNNING WITH COVERAGE")
    print("=" * 50)

    try:
        import coverage

        print("Coverage.py is available")
    except ImportError:
        print("Coverage.py not found. Install with:")
        print("pip install coverage")
        return False

    project_root = Path(__file__).parent.parent

    # Run pytest with coverage
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=nextjs_hydration_parser",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "tests/",
            "-v",
        ],
        cwd=project_root,
    )

    if result.returncode == 0:
        print("\n✓ Tests passed with coverage report generated")
        print("HTML coverage report: htmlcov/index.html")
        return True
    else:
        print("\n✗ Tests with coverage failed")
        return False


def main():
    """Main function"""

    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        success = run_coverage()
    else:
        success = run_tests()

        # Offer to run with coverage
        if success:
            response = input("\nRun with coverage report? (y/n): ").lower().strip()
            if response == "y":
                run_coverage()

    # Print additional information
    print("\n" + "=" * 50)
    print("ADDITIONAL INFORMATION")
    print("=" * 50)
    print("To run specific tests:")
    print("  pytest tests/test_basic.py -v")
    print("  pytest tests/test_search.py::TestKeyExtraction -v")
    print("  pytest tests/ -k 'test_simple' -v")
    print("\nTo run with coverage:")
    print("  python run_tests.py --coverage")
    print("\nTo run examples:")
    print("  python examples/basic_usage.py")
    print("  python examples/ecommerce_scraping.py")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

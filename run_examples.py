#!/usr/bin/env python3
"""
Example runner script for Next.js Hydration Parser

This script runs all examples to demonstrate the library's capabilities.
"""

import sys
import os
import importlib.util
import traceback
from pathlib import Path


def run_example(example_path):
    """Run a single example file"""

    try:
        print(f"\n{'='*60}")
        print(f"Running: {example_path.name}")
        print(f"{'='*60}")

        # Load and run the example module
        spec = importlib.util.spec_from_file_location("example", example_path)
        example = importlib.util.module_from_spec(spec)

        # Add the project root to sys.path so imports work
        project_root = example_path.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        spec.loader.exec_module(example)

        print(f"\n✓ {example_path.name} completed successfully")
        return True

    except ImportError as e:
        print(f"✗ Import error in {example_path.name}: {e}")
        print("Make sure the package is installed or run from the project root")
        return False

    except Exception as e:
        print(f"✗ Error running {example_path.name}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run all examples"""

    print("Next.js Hydration Parser - Example Runner")
    print("=" * 60)

    # Get examples directory
    project_root = Path(__file__).parent
    examples_dir = project_root / "examples"

    if not examples_dir.exists():
        print(f"ERROR: Examples directory not found: {examples_dir}")
        return False

    # Find all Python example files
    example_files = list(examples_dir.glob("*.py"))
    example_files.sort()

    if not example_files:
        print(f"No example files found in {examples_dir}")
        return False

    print(f"Found {len(example_files)} example files:")
    for f in example_files:
        print(f"  - {f.name}")

    # Run examples
    results = {}

    for example_file in example_files:
        success = run_example(example_file)
        results[example_file.name] = success

    # Print summary
    print(f"\n{'='*60}")
    print("EXAMPLE EXECUTION SUMMARY")
    print(f"{'='*60}")

    success_count = 0
    for filename, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {filename}")
        if success:
            success_count += 1

    print(f"\nResults: {success_count}/{len(results)} examples ran successfully")

    if success_count == len(results):
        print("🎉 All examples completed successfully!")
        return True
    else:
        print("❌ Some examples failed. Check output above for details.")
        return False


def run_interactive():
    """Run examples interactively"""

    examples_dir = Path(__file__).parent / "examples"
    example_files = list(examples_dir.glob("*.py"))
    example_files.sort()

    print("\nInteractive Example Runner")
    print("=" * 30)

    for i, example_file in enumerate(example_files, 1):
        print(f"{i}. {example_file.name}")

    while True:
        try:
            choice = input(
                f"\nSelect example (1-{len(example_files)}) or 'q' to quit: "
            ).strip()

            if choice.lower() == "q":
                break

            choice_num = int(choice)
            if 1 <= choice_num <= len(example_files):
                selected_file = example_files[choice_num - 1]
                run_example(selected_file)
            else:
                print(f"Please enter a number between 1 and {len(example_files)}")

        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive()
    else:
        success = main()

        if not success:
            print("\nTip: Try running examples individually:")
            print("  python examples/basic_usage.py")
            print("  python examples/ecommerce_scraping.py")
            print("\nOr run interactively:")
            print("  python run_examples.py --interactive")

        sys.exit(0 if success else 1)

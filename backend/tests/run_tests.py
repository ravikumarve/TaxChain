#!/usr/bin/env python3
"""
Test runner script for TaxChain backend.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py -v        # Run with verbose output
    python run_tests.py test_database_integration.py  # Run specific test
"""

import subprocess
import sys
import os


def run_tests():
    """Run pytest with proper configuration."""
    # Set test environment
    os.environ["ENVIRONMENT"] = "test"

    # Build pytest command
    cmd = [
        "python",
        "-m",
        "pytest",
        "-x",
        "-v",  # exit on first failure, verbose
        "--asyncio-mode=auto",
        "--cov=app",
        "--cov-report=term-missing",
    ]

    # Add specific test file if provided
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        cmd.append(".")

    # Run pytest
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())

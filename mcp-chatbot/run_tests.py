#!/usr/bin/env python3
"""
Test runner for AWS MCP Agent
"""

import unittest
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests and return results."""
    print("🧪 AWS MCP Agent - Test Suite")
    print("=" * 40)
    
    # Add src to path
    project_root = Path(__file__).parent
    src_path = project_root / 'src'
    sys.path.insert(0, str(src_path))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print(f"\n🔍 Discovering tests in: {start_dir}")
    print(f"📁 Source path: {src_path}")
    print(f"🧪 Running test suite...\n")
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️ Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Ready for production.")
        return True
    else:
        print("\n⚠️ Some tests failed. Please fix before production release.")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

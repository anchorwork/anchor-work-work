#!/usr/bin/env python3
"""
run_tests.py

Simple test runner for Anchorwork project tests.
"""
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory."""
    tests_dir = Path(__file__).parent / "tests"
    
    print("🧪 Running Anchorwork Tests")
    print("=" * 50)
    
    # Run pytest if available
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(tests_dir), 
            "-v", "--tb=short"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
            
    except FileNotFoundError:
        print("pytest not found, running individual test files...")
        
        # Fallback: run individual test files
        for test_file in tests_dir.glob("test_*.py"):
            print(f"\n📝 Running {test_file.name}...")
            try:
                result = subprocess.run([
                    sys.executable, str(test_file)
                ], cwd=Path(__file__).parent)
                
                if result.returncode == 0:
                    print(f"✅ {test_file.name} passed")
                else:
                    print(f"❌ {test_file.name} failed")
                    
            except Exception as e:
                print(f"❌ Error running {test_file.name}: {e}")

if __name__ == "__main__":
    run_tests()

# Anchorwork Tests

This directory contains all test files for the Anchorwork project.

## Test Files

### API Tests
- `test_api_integration.py` - Tests for API endpoints integration
- `test_all_endpoints.py` - Comprehensive endpoint testing
- `test_enhanced_api.py` - Enhanced API functionality tests

### Dashboard Tests
- `test_dashboard.py` - Dashboard UI and functionality tests

### Memory & Redis Tests
- `test_enhanced_memory.py` - Enhanced memory system tests
- `test_redis_migration.py` - Redis migration verification tests
- `test_redis_streams.py` - Redis streams functionality tests
- `test_hybrid_logging.py` - Hybrid logging system tests

### System Tests
- `test_smoke.py` - Basic smoke tests
- `test_phase1.sh` - Phase 1 system tests (shell script)

## Running Tests

### Run All Tests
```bash
# From the project root
python run_tests.py
```

### Run Individual Tests
```bash
# Run a specific test file
python tests/test_smoke.py

# Run with pytest (if installed)
python -m pytest tests/test_smoke.py -v
```

### Run Redis Tests
```bash
# Test Redis migration
python tests/test_redis_migration.py

# Test Redis streams
python tests/test_redis_streams.py
```

## Test Dependencies

Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development dependencies
```

## Notes

- Redis tests require a running Redis server
- API tests may require the main application to be running
- Some tests may create temporary files in `/tmp` or the project directory

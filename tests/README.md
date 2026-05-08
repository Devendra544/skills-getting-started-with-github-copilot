# Tests Directory

This directory contains comprehensive FastAPI tests for the Mergington High School API.

## Running Tests

To run the test suite:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_app.py

# Run specific test class
pytest tests/test_app.py::TestSignupEndpoint

# Run specific test method
pytest tests/test_app.py::TestSignupEndpoint::test_signup_successful
```

## Test Coverage

The test suite covers:

- **Root endpoint**: Redirect functionality
- **Activities endpoint**: Retrieving all activities
- **Signup endpoint**: Successful signups, error cases, edge cases
- **Unregister endpoint**: Successful unregisters, error cases
- **Integration scenarios**: Complete workflows
- **Edge cases**: Special characters, long emails, unicode

## Test Structure

- `conftest.py`: Pytest fixtures and configuration
- `test_app.py`: Main test suite covering all endpoints
- `__init__.py`: Makes tests a Python package

## Fixtures

- `client`: FastAPI test client
- `reset_activities`: Resets activities database between tests
- `sample_email`: Sample email for testing
- `existing_participant`: Email of existing participant
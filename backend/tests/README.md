# TaxChain Backend Tests

This directory contains tests for the TaxChain backend database models and functionality.

## Test Files

### `test_database_unit.py`
Unit tests that don't require a live database connection. These tests:
- Validate model definitions and relationships
- Test Decimal precision handling for financial calculations
- Verify relationship mappings work correctly
- Test schema validation (skipped for SQLite, requires PostgreSQL)

### `test_database_integration.py`
Integration tests that require a live PostgreSQL database. These tests:
- Test actual database connectivity
- Create and query real database records
- Test async session functionality
- Verify Decimal precision in actual database operations
- Test concurrent database operations

## Running Tests

### Unit Tests (No Database Required)
```bash
cd /home/matrix/Desktop/TaxChain/backend
source venv/bin/activate
PYTHONPATH=. python tests/test_database_unit.py
```

### Integration Tests (Requires PostgreSQL)
1. Ensure PostgreSQL is running
2. Create a test database:
   ```sql
   CREATE DATABASE taxchain_test;
   ```
3. Run the tests:
   ```bash
   cd /home/matrix/Desktop/TaxChain/backend
   source venv/bin/activate
   PYTHONPATH=. python tests/test_database_integration.py
   ```

### Using pytest
```bash
cd /home/matrix/Desktop/TaxChain/backend
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_database_unit.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Test Environment

### Environment Variables
Create a `.env` file in the backend directory with:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/taxchain_test
SECRET_KEY=test-jwt-secret-min-32-chars-here-1234567890
# ... other required variables
```

### Dependencies
Make sure all test dependencies are installed:
```bash
pip install pytest pytest-asyncio asyncpg
```

## Test Coverage

The tests cover:

1. **Model Definitions**
   - Field types and constraints
   - Default values
   - Relationship mappings

2. **Decimal Precision**
   - Financial calculations with high precision
   - 36,18 precision for crypto amounts
   - 20,8 precision for USD values

3. **Relationships**
   - User ↔ Wallet (one-to-many)
   - User ↔ Transaction (one-to-many)
   - Wallet ↔ Transaction (one-to-many)

4. **Database Operations**
   - Async session management
   - Connection pooling
   - Transaction handling

## Writing New Tests

Follow these patterns:

### Unit Tests
```python
def test_model_creation():
    """Test model instantiation and field validation."""
    obj = Model(field="value")
    assert obj.field == "value"
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_database_operation():
    """Test actual database operations."""
    async with AsyncSession(engine) as session:
        obj = Model(field="value")
        session.add(obj)
        await session.commit()
        assert obj.id is not None
```

## Notes

- Use `Decimal` for all financial calculations
- Test edge cases with very small/large numbers
- Verify relationships work bidirectionally
- Clean up test data after each test
- Use async/await for database operations
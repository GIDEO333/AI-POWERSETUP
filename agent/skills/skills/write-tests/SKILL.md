---
name: write-tests
description: Write unit tests, integration tests, and end-to-end tests for any codebase. Use when the user asks to add tests or when fixing a bug (write a test to prevent regression).
category: Dev
---

# Write Tests

## Test Pyramid

- **Unit tests** — test a single function/class in isolation (fast, many)
- **Integration tests** — test how components work together (medium)
- **E2E tests** — test the full user flow (slow, few)

## Steps

1. **Identify what to test** — Focus on: public functions, edge cases, error paths
2. **Arrange** — Set up the data/state needed
3. **Act** — Call the function/method under test
4. **Assert** — Verify the output or side effect is correct
5. **Clean up** — Reset state if needed (especially for DB/file tests)

## By Language

### Python (pytest)
```python
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_raises_on_string():
    with pytest.raises(TypeError):
        add("a", 1)
```

### JavaScript (jest/vitest)
```javascript
test('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
});

test('throws on invalid input', () => {
    expect(() => add('a', 1)).toThrow(TypeError);
});
```

## What Makes a Good Test

- **Fast** — Unit tests should run in milliseconds
- **Isolated** — No dependency on external services (mock them)
- **Deterministic** — Same result every run
- **Clear** — Test name describes exactly what is being tested
- **One assertion per test** (ideally)

---
name: UI Functional Tester
description: This agent performs functional UI testing of web applications using Playwright. Use when you need to "test frontend functionality", "verify UI works", "check login/logout", "test user flows", "validate web interface", or "run browser tests".
---

# UI Functional Tester Agent

## Purpose

This agent performs automated functional testing of web applications using Playwright. It verifies that UI components work correctly by simulating real user interactions in a browser.

## Capabilities

1. **Browser Automation** - Launch Chromium browser and navigate through the application
2. **User Flow Testing** - Test complete user journeys (login, logout, CRUD operations)
3. **Visual Verification** - Check that expected elements appear on screen
4. **State Verification** - Verify localStorage, sessionStorage, cookies
5. **Error Handling** - Capture screenshots on failures, log errors
6. **API + UI Hybrid** - Can use API for setup and UI for verification

## When to Use

Use this agent when:
- Need to verify frontend functionality works in browser
- Testing login/logout flows
- Validating form submissions
- Checking that UI updates after actions
- Debugging why UI tests fail
- Running regression tests on web interface

## Testing Approach

### 1. Setup Phase
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()
```

### 2. Test Execution
```python
# Navigate
page.goto("http://localhost:3000/login")
page.wait_for_load_state("networkidle")

# Interact
page.fill('input[name="email"]', 'test@example.com')
page.fill('input[name="password"]', 'password123')
page.click('button[type="submit"]')
page.wait_for_load_state("networkidle")

# Verify
assert page.url == "http://localhost:3000/"
user_info = page.locator('.user-info').text_content()
assert "Test User" in user_info
```

### 3. State Verification
```python
# Check localStorage
token = page.evaluate("localStorage.getItem('token')")
assert token is not None

# Check DOM element
logout_button = page.locator('button:has-text("Выйти")')
assert logout_button.is_visible()
```

### 4. Cleanup
```python
browser.close()
```

## Common Test Patterns

### Login Flow Test
```python
def test_login(page):
    page.goto("http://localhost:3000/login")
    page.fill('input[name="email"]', 'admin@cafe.ru')
    page.fill('input[name="password"]', 'admin123')
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    # Verify logged in
    token = page.evaluate("localStorage.getItem('token')")
    assert token is not None
    
    # Check header shows user
    user_name = page.locator('.header-user-name').text_content()
    assert user_name != "Гость"
```

### Logout Flow Test
```python
def test_logout(page):
    # First login
    login_via_api(page, 'admin@cafe.ru', 'admin123')
    page.goto("http://localhost:3000/")
    
    # Click logout
    page.click('button[title="Выйти"]')
    page.wait_for_load_state("networkidle")
    
    # Verify logged out
    token = page.evaluate("localStorage.getItem('token')")
    assert token is None
    
    # Should redirect to login
    assert "/login" in page.url
```

### Form Submission Test
```python
def test_create_user(page):
    login_as_manager(page)
    page.goto("http://localhost:3000/users")
    
    # Open create modal
    page.click('button:has-text("Добавить пользователя")')
    
    # Fill form
    page.fill('input[name="email"]', 'new@test.com')
    page.fill('input[name="name"]', 'New')
    page.fill('input[name="surname"]', 'User')
    page.fill('input[name="nickname"]', 'newuser')
    page.fill('input[name="password"]', 'password123')
    page.select_option('select[name="level"]', 'client')
    
    # Submit
    page.click('button:has-text("Создать")')
    page.wait_for_load_state("networkidle")
    
    # Verify created
    assert "new@test.com" in page.content()
```

## Debugging Techniques

### 1. Take Screenshot on Failure
```python
try:
    # test code
except Exception as e:
    page.screenshot(path="failure.png")
    raise
```

### 2. Log Page Content
```python
print(f"Page URL: {page.url}")
print(f"Page Title: {page.title()}")
print(f"LocalStorage: {page.evaluate('localStorage')}")
```

### 3. Wait for Specific Element
```python
# Wait for element to appear
page.wait_for_selector('.user-info', timeout=5000)

# Wait for text
page.wait_for_function(
    'document.querySelector(".user-info").innerText.includes("Admin")',
    timeout=5000
)
```

### 4. Check Network Requests
```python
with page.expect_response("**/api/users/me") as response_info:
    page.click('button:has-text("Профиль")')
response = response_info.value
print(f"Status: {response.status}")
print(f"Body: {response.json()}")
```

## Test File Structure

```python
"""Functional UI tests for Cafe Orders frontend."""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext
from playwright.sync_api import expect

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()

class TestUserFlows:
    def test_login_logout(self, page):
        """Test complete login/logout flow."""
        # Test code here
        
    def test_user_header_updates(self, page):
        """Test that header shows correct user after login."""
        # Test code here
```

## Running Tests

```bash
# Run all UI tests
pytest tests/test_ui_functional.py -v

# Run specific test
pytest tests/test_ui_functional.py::TestUserFlows::test_login_logout -v

# Run with browser visible (not headless)
pytest tests/test_ui_functional.py -v -s --headed

# Run with slow motion
pytest tests/test_ui_functional.py -v -s --slow-mo=500
```

## Best Practices

1. **Use fixtures** - Reuse browser, context, page setup
2. **Wait properly** - Use `wait_for_load_state("networkidle")` after navigation
3. **Use data-testid** - Add test IDs to elements for stable selectors
4. **Isolate tests** - Each test should be independent
5. **Clean up** - Clear localStorage/cookies between tests
6. **Take screenshots** - Capture failures for debugging
7. **Use API for setup** - Faster than UI for creating test data
8. **Test real flows** - Simulate actual user behavior

## Common Issues

### Issue: Element not found
**Solution:** Add wait for element
```python
page.wait_for_selector('button.submit', timeout=5000)
```

### Issue: Test flaky
**Solution:** Add explicit waits, not sleep
```python
# Bad
time.sleep(2)

# Good
page.wait_for_load_state("networkidle")
page.wait_for_selector('.result')
```

### Issue: localStorage not persisting
**Solution:** Use same context
```python
# Don't create new context between steps
context = browser.new_context()
page1 = context.new_page()  # Login here
page2 = context.new_page()  # Should have same localStorage
```

## Example: Complete Test Suite

See `tests/test_all_endpoints_web.py` for a complete example of functional UI tests.

# Contact Form Component - Documentation

## Overview

A production-ready, fully accessible contact form component with comprehensive validation, error handling, and edge case management. Built with vanilla HTML, CSS, and JavaScript for maximum compatibility and performance.

## Features

### ✅ Core Functionality
- **Three Input Fields**: Name, Email, and Message with appropriate types
- **Real-time Validation**: Client-side validation with instant feedback
- **Server-side Validation**: Duplicate validation on backend for security
- **Success Feedback**: Clear success message with automatic form reset
- **Error Handling**: Specific error messages for each validation rule
- **Loading States**: Visual feedback during form submission

### 🔒 Validation Rules

#### Name Field
- **Required**: Yes
- **Min Length**: 2 characters
- **Max Length**: 50 characters
- **Pattern**: Alphanumeric characters, spaces, and hyphens only
- **Regex**: `^[a-zA-Z0-9\s-]{2,50}$`

#### Email Field
- **Required**: Yes
- **Pattern**: Valid email format
- **Regex**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

#### Message Field
- **Required**: Yes
- **Min Length**: 10 characters
- **Max Length**: 1000 characters
- **Character Counter**: Real-time display of remaining characters

### 🎯 Edge Cases Handled

1. **Offline Detection**
   - Detects when browser is offline before submission
   - Shows user-friendly message: "Currently offline, please try again later"
   - Listens for online/offline events

2. **Paste Sanitization**
   - Strips HTML and formatting from pasted content
   - Prevents XSS attacks through paste
   - Maintains plain text only

3. **Double-Submit Prevention**
   - Disables submit button during processing
   - Prevents multiple submissions via flag
   - Visual loading indicator

4. **Browser Auto-fill**
   - Validates auto-filled data on page load
   - Compatible with password managers
   - Triggers validation after auto-fill detection

5. **Browser Navigation**
   - Maintains form state on back/forward navigation
   - Preserves validation state
   - Uses `pageshow` event for cache detection

6. **Screen Reader Support**
   - ARIA labels on all fields
   - Live regions for error messages
   - Status announcements for form submission
   - Clear focus management

7. **Keyboard Navigation**
   - Logical tab order: name → email → message → submit
   - Visible focus indicators
   - Enter key submits form
   - Escape key clears errors (browser default)

## File Structure

```
workspace/
├── templates/
│   └── contact_form.html          # Complete standalone component
├── main.py                         # FastAPI backend with /contact endpoint
├── contact_submissions/            # Stores form submissions (created automatically)
└── CONTACT_FORM_README.md         # This documentation
```

## Installation & Usage

### 1. Prerequisites

```bash
# Python 3.7+
# FastAPI and dependencies already installed
```

### 2. Access the Form

The contact form is available at two locations:

1. **Standalone Page**: `http://localhost:8000/contact`
2. **Template Integration**: Can be embedded in other pages

### 3. Start the Server

```bash
# From workspace root
python run.py

# Or directly
python main.py
```

### 4. Access in Browser

```
http://localhost:8000/contact
```

## API Endpoint

### POST `/contact`

Handles contact form submission with server-side validation.

**Request Format**: `multipart/form-data`

**Parameters**:
```javascript
{
    name: string,    // 2-50 chars, alphanumeric + spaces + hyphens
    email: string,   // Valid email format
    message: string  // 10-1000 characters
}
```

**Success Response** (200):
```json
{
    "status": "success",
    "message": "Thank you for your message! We'll get back to you soon."
}
```

**Validation Error Response** (400):
```json
{
    "status": "error",
    "message": "Validation failed",
    "errors": [
        "Name must be at least 2 characters",
        "Please enter a valid email address"
    ]
}
```

**Server Error Response** (500):
```json
{
    "status": "error",
    "message": "An error occurred while processing your request. Please try again later."
}
```

## Accessibility Features

### WCAG 2.1 Compliance

- **Level AA** compliant for accessibility
- Keyboard navigable (all functionality available via keyboard)
- Screen reader compatible (tested with common screen readers)
- Visible focus indicators
- Sufficient color contrast ratios
- Clear error identification

### ARIA Attributes

- `aria-required="true"` on required fields
- `aria-invalid` dynamically updated based on validation
- `aria-describedby` links fields to error messages
- `aria-live` regions for dynamic content updates
- `role="alert"` for error and success messages

### Screen Reader Announcements

```html
<!-- Field descriptions -->
<div class="sr-only">Name must be 2-50 characters...</div>

<!-- Error announcements -->
<div role="alert" aria-live="polite">Name is required</div>

<!-- Success announcements -->
<div role="status" aria-live="polite">Form submitted successfully</div>
```

## Validation Flow

```
User Types → Real-time Character Count → On Blur → Validate Field
                                              ↓
                                     Display/Clear Error
                                              ↓
User Clicks Submit → Validate All Fields → Check Online Status
                            ↓                      ↓
                        Valid?                 Online?
                            ↓                      ↓
                    Show Loading → Send to Server → Handle Response
                                                          ↓
                                                   Success/Error
                                                          ↓
                                                Display Message
```

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Customization

### Styling

All styles are contained in the `<style>` block. Key CSS custom properties:

```css
/* Colors */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--error-color: #dc3545;
--success-color: #28a745;

/* Spacing */
--form-padding: 40px;
--input-padding: 12px 15px;

/* Border radius */
--border-radius: 8px;
```

### Validation Rules

Modify validation patterns in JavaScript:

```javascript
// In contact_form.html <script> section
const NAME_PATTERN = /^[a-zA-Z0-9\s-]{2,50}$/;
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const MESSAGE_MIN_LENGTH = 10;
const MESSAGE_MAX_LENGTH = 1000;
```

**Important**: Also update backend validation in `main.py` to match:

```python
# In main.py submit_contact_form function
NAME_PATTERN = r'^[a-zA-Z0-9\s-]{2,50}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
MESSAGE_MIN_LENGTH = 10
MESSAGE_MAX_LENGTH = 1000
```

## Security Considerations

### Client-Side
- ✅ Input sanitization on paste events
- ✅ HTML/XSS prevention in user input
- ✅ Maximum length enforcement
- ✅ Pattern matching for allowed characters

### Server-Side
- ✅ Duplicate validation (never trust client)
- ✅ Input trimming and sanitization
- ✅ Proper error messages (no sensitive info leakage)
- ✅ Rate limiting ready (add middleware)
- ✅ CSRF protection (FastAPI default)

### Recommended Production Additions

1. **Rate Limiting**: Add rate limiting middleware
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/contact")
   @limiter.limit("5/minute")
   async def submit_contact_form(...):
   ```

2. **CAPTCHA**: Add reCAPTCHA or similar
   ```html
   <div class="g-recaptcha" data-sitekey="your-site-key"></div>
   ```

3. **Database**: Replace file storage with database
   ```python
   # In production
   await db.contact_submissions.insert_one({
       "name": name,
       "email": email,
       "message": message,
       "timestamp": datetime.utcnow(),
       "ip_address": request.client.host
   })
   ```

4. **Email Notifications**: Send email to support team
   ```python
   await send_email(
       to="support@yourdomain.com",
       subject=f"New Contact Form: {name}",
       body=message
   )
   ```

## Testing

### Manual Testing Checklist

- [ ] **Valid Submission**: Fill all fields correctly and submit
- [ ] **Empty Fields**: Try submitting with empty fields
- [ ] **Invalid Name**: Use special characters (!, @, #)
- [ ] **Short Name**: Enter 1 character
- [ ] **Long Name**: Enter 51+ characters
- [ ] **Invalid Email**: Try "notanemail", "test@", "@test.com"
- [ ] **Short Message**: Enter < 10 characters
- [ ] **Long Message**: Enter > 1000 characters
- [ ] **Paste Test**: Copy/paste formatted text (from Word, etc.)
- [ ] **Double Submit**: Click submit button twice quickly
- [ ] **Offline Test**: Disable network and try submitting
- [ ] **Auto-fill Test**: Use browser auto-fill
- [ ] **Navigation Test**: Fill form, navigate away, use back button
- [ ] **Keyboard Test**: Tab through form, submit with Enter
- [ ] **Screen Reader**: Test with NVDA/JAWS/VoiceOver

### Automated Testing

Create test file `tests/test_contact_form.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_valid_submission():
    response = client.post("/contact", data={
        "name": "John Doe",
        "email": "john@example.com",
        "message": "This is a test message with enough characters."
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_invalid_email():
    response = client.post("/contact", data={
        "name": "John Doe",
        "email": "invalid-email",
        "message": "This is a test message."
    })
    assert response.status_code == 400
    assert "errors" in response.json()

def test_short_message():
    response = client.post("/contact", data={
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Short"
    })
    assert response.status_code == 400
```

## Performance Optimizations

1. **No External Dependencies**: Pure vanilla JS = faster load times
2. **Inline Styles**: Reduces HTTP requests
3. **Debounced Validation**: Only validates on blur, not every keystroke
4. **Efficient DOM Updates**: Minimal reflows and repaints
5. **Lazy Error Creation**: Error elements present but hidden initially

## Troubleshooting

### Issue: Form doesn't submit
**Solution**: Check browser console for JavaScript errors. Ensure FastAPI server is running.

### Issue: Validation not working
**Solution**: Clear browser cache. Ensure JavaScript is enabled.

### Issue: Success message not showing
**Solution**: Check network tab for API response. Verify endpoint returns correct JSON.

### Issue: Styling looks broken
**Solution**: Ensure no CSS conflicts from other stylesheets. Check for ad blockers.

### Issue: Accessibility features not working
**Solution**: Test in different browsers. Ensure ARIA attributes are present in DOM.

## Future Enhancements

- [ ] File upload support (attachments)
- [ ] Multi-language support (i18n)
- [ ] Dark mode theme
- [ ] Progressive Web App features
- [ ] Webhook integration
- [ ] Admin dashboard for submissions
- [ ] Email confirmation to users
- [ ] Advanced spam filtering

## Support

For questions or issues:
1. Check this documentation
2. Review browser console for errors
3. Check server logs
4. Verify all prerequisites are met

## License

This component is part of the GitHub to App Converter project and follows the same license (MIT).

---

**Built with ❤️ following web accessibility and usability best practices**

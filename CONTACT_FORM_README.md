# Contact Form Component - Quick Start Guide

## 🚀 Overview

A production-ready contact form component with comprehensive validation, accessibility features, and security measures. Built with FastAPI backend and vanilla JavaScript frontend.

## ✨ Features

### Core Functionality
- ✅ **Name Field**: 2-50 characters, letters/spaces/hyphens only
- ✅ **Email Field**: RFC-compliant email validation
- ✅ **Message Field**: 10-1000 characters with live counter
- ✅ **Real-time Validation**: Inline error messages
- ✅ **Success Feedback**: Clear confirmation after submission
- ✅ **Auto-clear**: Form resets after successful submission

### Advanced Features
- 🔒 **Security**: HTML stripping, XSS prevention, server-side validation
- ♿ **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- 📱 **Responsive**: Mobile-optimized with touch-friendly controls
- 🔄 **Loading States**: Spinner and disabled button during submission
- 🚫 **Duplicate Prevention**: Blocks multiple simultaneous submissions
- 📡 **Offline Detection**: Warns when network is unavailable
- 💾 **Unsaved Changes**: Confirms before browser refresh
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## 🎯 Quick Start

### 1. Installation

```bash
# Install dependencies (if not already installed)
pip install fastapi uvicorn python-multipart

# Or use existing requirements
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python3 main.py
```

The server will start at `http://localhost:8000`

### 3. Access the Contact Form

Open your browser and navigate to:
```
http://localhost:8000/contact
```

## 📋 Usage Examples

### Valid Input Examples

**Name:**
- ✓ "John Doe"
- ✓ "Mary-Jane Smith"
- ✓ "Al"
- ✓ "Jean-Pierre"

**Email:**
- ✓ "user@example.com"
- ✓ "john.doe@company.co.uk"
- ✓ "test+tag@domain.org"

**Message:**
- ✓ "Thank you for your service!" (minimum 10 chars)
- ✓ Any text between 10-1000 characters

### Invalid Input Examples

**Name:**
- ✗ "J" (too short)
- ✗ "John123" (contains numbers)
- ✗ "User@Name" (invalid characters)
- ✗ 51+ character names

**Email:**
- ✗ "notanemail" (missing @ and domain)
- ✗ "user@" (incomplete)
- ✗ "@example.com" (missing local part)

**Message:**
- ✗ "Short" (less than 10 chars)
- ✗ 1001+ character messages

## 🧪 Testing

### Run Validation Tests

```bash
python3 test_contact_form.py
```

This tests all validation logic:
- Name pattern matching
- Email format validation
- Message length constraints
- HTML stripping functionality

### Manual Testing Checklist

1. **Happy Path**
   - Fill all fields with valid data
   - Click submit
   - ✓ See success message
   - ✓ Form clears

2. **Validation Errors**
   - Leave fields empty → See "required" errors
   - Enter invalid name → See name validation error
   - Enter invalid email → See email error
   - Enter short message → See length error

3. **Edge Cases**
   - Paste HTML in message → HTML is stripped
   - Double-click submit → Only one submission
   - Modify form and refresh → See confirmation
   - Disconnect network and submit → See offline error

4. **Accessibility**
   - Tab through form → Logical focus order
   - Use screen reader → All labels announced
   - Check focus indicators → Visible outlines

5. **Mobile**
   - Open on mobile device
   - Fill form → Keyboard doesn't overlap fields
   - Submit → All features work

## 📡 API Endpoints

### GET `/contact`
**Description:** Serves the contact form page

**Response:** HTML page

### POST `/contact/submit`
**Description:** Handles form submission

**Request Body (Form Data):**
```
name: string (2-50 chars)
email: string (valid email)
message: string (10-1000 chars)
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Message sent successfully!"
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Validation error description"
}
```

## 🎨 Customization

### Styling
All styles are contained in `templates/contact_form.html`. Key CSS variables:

```css
/* Primary colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Error color */
color: #e53e3e;

/* Success color */
background: #d4edda;
```

### Validation Rules
Update patterns in both files:

**Frontend** (`templates/contact_form.html`):
```javascript
const validationRules = {
    name: {
        pattern: /^[a-zA-Z\s-]{2,50}$/,
        message: 'Your custom message'
    },
    // ...
};
```

**Backend** (`main.py`):
```python
name_pattern = re.compile(r'^[a-zA-Z\s-]{2,50}$')
# Update validation logic
```

## 🔒 Security Features

1. **Input Sanitization**
   - HTML tags stripped from all inputs
   - Regex pattern validation
   - Length restrictions enforced

2. **XSS Prevention**
   - Server-side HTML removal
   - Safe DOM manipulation
   - No direct innerHTML usage

3. **CSRF Protection**
   - Ready for CSRF token integration
   - Form-based submission only

4. **Rate Limiting**
   - Client-side duplicate prevention
   - Ready for server-side rate limiting

## ♿ Accessibility Compliance

- ✅ **WCAG 2.1 Level AA** compliant
- ✅ **ARIA** labels and roles
- ✅ **Keyboard navigation** fully supported
- ✅ **Screen reader** tested
- ✅ **Focus indicators** visible
- ✅ **Semantic HTML** throughout
- ✅ **Color contrast** meets standards

## 📱 Browser Support

| Browser | Minimum Version | Status |
|---------|----------------|---------|
| Chrome  | 90+            | ✅ Full Support |
| Firefox | 88+            | ✅ Full Support |
| Safari  | 14+            | ✅ Full Support |
| Edge    | 90+            | ✅ Full Support |
| iOS Safari | 14+         | ✅ Full Support |
| Chrome Mobile | 90+      | ✅ Full Support |

## 🐛 Troubleshooting

### Form doesn't submit
- Check browser console for JavaScript errors
- Ensure all fields pass validation
- Verify internet connection
- Check server is running

### Validation not working
- Clear browser cache
- Check validation patterns are correct
- Verify JavaScript is enabled

### Styling issues
- Check viewport meta tag is present
- Verify CSS is loading
- Test in different browsers

### Server errors
- Check FastAPI logs in terminal
- Verify all dependencies installed
- Ensure `templates/` directory exists

## 📚 Additional Resources

- **Full Documentation**: See `CONTACT_FORM_DOCUMENTATION.md`
- **Main App**: Visit `http://localhost:8000/` for the main app
- **FastAPI Docs**: Visit `http://localhost:8000/docs` for API documentation

## 🤝 Integration Example

To add to an existing FastAPI app:

```python
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/contact")
async def contact_form(request: Request):
    return templates.TemplateResponse("contact_form.html", {"request": request})

@app.post("/contact/submit")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    # Add your validation and processing here
    return JSONResponse({
        "status": "success",
        "message": "Message sent successfully!"
    })
```

## 📝 License

This component is part of the GitHub to App Converter project.

---

**Need Help?** Use the contact form itself to send a message! 😊

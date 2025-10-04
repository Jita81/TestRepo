# Contact Form - Quick Start Guide

## 🚀 Getting Started (60 seconds)

### 1. Start the Server
```bash
python3 main.py
```

### 2. Access the Form
Open browser and navigate to:
```
http://localhost:8000/contact
```

Or click "Contact Us" button on the home page:
```
http://localhost:8000/
```

### 3. Test the Form
Fill in the form:
- **Name**: John Smith (2-50 chars)
- **Email**: john@example.com (valid email)
- **Message**: Your message here (10-1000 chars)

Click "Send Message" → See success message!

---

## ✅ Quick Validation Reference

| Field | Min | Max | Type | Required |
|-------|-----|-----|------|----------|
| Name | 2 | 50 | Text | Yes |
| Email | - | - | Email | Yes |
| Message | 10 | 1000 | Text | Yes |

---

## 🧪 Run Tests

```bash
# Terminal 1: Start server
python3 main.py

# Terminal 2: Run tests
python3 test_contact_form.py
```

Expected output: ✨ All tests passed successfully!

---

## 📱 Mobile Testing

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (iPhone, Android)
4. Test form on mobile viewport
5. Verify touch targets ≥44px

---

## ♿ Accessibility Testing

### Keyboard Navigation
- **Tab** - Move to next field
- **Shift+Tab** - Move to previous field
- **Enter** - Submit form
- Verify focus indicators are visible

### Screen Reader Testing
- Use NVDA (Windows) or VoiceOver (Mac)
- Navigate through form
- Verify all labels and errors are announced

---

## 🔒 Security Verification

### Test XSS Prevention
Try submitting:
```
Name: <script>alert('XSS')</script>
Email: test@example.com
Message: <script>alert('XSS')</script> Test message
```

✅ Should succeed with sanitized input (no script execution)

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Or use different port
uvicorn main:app --port 8001
```

### Missing dependencies
```bash
pip install fastapi uvicorn python-multipart jinja2
```

### Template not found
```bash
# Verify template exists
ls -la templates/contact.html
```

---

## 📚 Documentation

- **Full Docs**: See `CONTACT_FORM_DOCUMENTATION.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`
- **Tests**: See `test_contact_form.py`
- **Source**: See `templates/contact.html` and `main.py`

---

## 🎯 Key Features

✅ Real-time validation
✅ Loading spinner
✅ Success/error messages
✅ Character counter
✅ XSS prevention
✅ WCAG 2.1 AA compliant
✅ Mobile-friendly
✅ Screen reader support

---

## 💡 Common Use Cases

### Valid Submission
```
Name: Alice Johnson
Email: alice@company.com
Message: I have a question about your service.
```
Result: ✅ Success message + form clears

### Invalid Email
```
Name: Bob Smith
Email: invalid@email
Message: This is a test message.
```
Result: ❌ "Please enter a valid email address"

### Message Too Short
```
Name: Charlie Brown
Email: charlie@example.com
Message: Hi
```
Result: ❌ "Message must be at least 10 characters"

---

## 🔗 Quick Links

- **Home Page**: http://localhost:8000/
- **Contact Form**: http://localhost:8000/contact
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)

---

## ✨ Next Steps

1. ✅ Test all form validations
2. ✅ Verify accessibility features
3. ✅ Check mobile responsiveness
4. 📧 Add email integration (production)
5. 💾 Add database storage (production)
6. 🤖 Add CAPTCHA (production)

---

**Need Help?** Check the full documentation files for detailed information.

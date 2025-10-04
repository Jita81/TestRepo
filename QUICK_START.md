# Contact Form - Quick Start Guide

## Installation

```bash
# Install all dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py file directly
python3 main.py
```

## Accessing the Contact Form

Open your browser and navigate to:
```
http://localhost:8000/contact
```

## Testing the Form

### Valid Submission Example
```javascript
// Name: John Doe (2-50 characters)
// Email: john@example.com (valid format)
// Message: Hello there (10-1000 characters)
```

### Try These Edge Cases

1. **Unicode Names**: José García, François Müller, 李明
2. **Whitespace**: Try submitting with only spaces in message
3. **Special Characters**: Try < > @ in name field
4. **Long Message**: Type 1000+ characters
5. **Invalid Email**: test@, @example.com, no-domain
6. **Offline Mode**: Disable network and try to submit

## API Endpoint

### POST /api/contact

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello there, this is a test message."
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Message sent successfully"
}
```

**Error Response (422):**
```json
{
  "detail": {
    "status": "error",
    "message": "Name must be at least 2 characters"
  }
}
```

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest test_contact_form.py -v

# Run specific tests
pytest test_contact_form.py::TestContactFormValidation -v
pytest test_contact_form.py::TestContactFormEdgeCases -v
```

## Features Checklist

✅ Name field (2-50 characters)  
✅ Email field (valid format)  
✅ Message field (10-1000 characters)  
✅ Real-time validation  
✅ Loading spinner on submit  
✅ Prevents double-submission  
✅ Offline detection  
✅ XSS prevention  
✅ Unicode support  
✅ Accessibility (ARIA)  
✅ Error messages  
✅ Success messages  
✅ Character counter  
✅ Paste handling  
✅ Browser autofill support  

## File Structure

```
/workspace/
├── main.py                          # FastAPI backend with /api/contact endpoint
├── templates/
│   └── contact.html                 # Contact form UI component
├── test_contact_form.py             # 29 comprehensive tests
├── CONTACT_FORM_DOCUMENTATION.md    # Full documentation
├── QUICK_START.md                   # This file
└── requirements.txt                 # Dependencies
```

## Next Steps for Production

1. **Configure Email Sending**
   - Add SMTP configuration
   - Install: `pip install fastapi-mail`
   - Update endpoint to send emails

2. **Add Database Storage**
   - Install: `pip install sqlalchemy`
   - Create Contact model
   - Save submissions to database

3. **Enable Rate Limiting**
   - Install: `pip install slowapi`
   - Limit to 5 submissions per minute

4. **Add CAPTCHA**
   - Integrate Google reCAPTCHA
   - Prevent spam submissions

5. **Deploy**
   - Use HTTPS
   - Set up monitoring
   - Configure logging

## Troubleshooting

### Form not loading?
- Check if server is running: `curl http://localhost:8000/contact`
- Check browser console for errors

### Validation not working?
- Check browser console for JavaScript errors
- Verify API endpoint is accessible

### Can't submit form?
- Check network tab in browser dev tools
- Verify /api/contact endpoint returns 200 or 422

## Support

See `CONTACT_FORM_DOCUMENTATION.md` for detailed information.

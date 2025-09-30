# Contact Form

A production-ready contact form implementation with comprehensive validation, error handling, and testing.

## Features

- ✅ **Server-side validation** with Pydantic models
- ✅ **Client-side validation** with real-time feedback
- ✅ **RESTful API** built with FastAPI
- ✅ **Modern, responsive UI** with clean design
- ✅ **Comprehensive error handling** at all layers
- ✅ **Full test coverage** with unit and integration tests
- ✅ **Input sanitization** and security best practices
- ✅ **Detailed documentation** and examples

## Architecture

```
contact_form/
├── models.py           # Pydantic data models and validation
├── api.py              # FastAPI endpoints and business logic
├── static/
│   ├── contact_form.html  # Frontend UI
│   └── contact_form.js    # Client-side validation and API integration
├── tests/
│   ├── test_models.py     # Model validation tests
│   └── test_api.py        # API integration tests
└── README.md
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn pydantic[email] pytest pytest-asyncio httpx

# Or use the requirements file
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the server
uvicorn contact_form.api:app --reload

# The API will be available at:
# - Main API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Contact form: http://localhost:8000/static/contact_form.html
```

### Running Tests

```bash
# Run all tests
pytest contact_form/tests/ -v

# Run with coverage
pytest contact_form/tests/ --cov=contact_form --cov-report=html

# Run specific test file
pytest contact_form/tests/test_models.py -v
```

## API Documentation

### Submit Contact Form

**Endpoint:** `POST /api/contact`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "message": "This is my message with at least 10 characters."
}
```

**Validation Rules:**
- `name`: 2-100 characters, letters, spaces, hyphens, and apostrophes only
- `email`: Valid email format
- `message`: 10-2000 characters

**Success Response (201):**
```json
{
  "success": true,
  "message": "Your message has been received. We'll get back to you soon!",
  "submission_id": "abc123def456",
  "timestamp": "2025-09-30T12:00:00"
}
```

**Error Response (422):**
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "email": ["Invalid email format"]
  },
  "error_code": "VALIDATION_ERROR"
}
```

### Health Check

**Endpoint:** `GET /api/health`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-30T12:00:00"
}
```

## Usage Examples

### Python Client

```python
import requests

# Submit contact form
response = requests.post(
    "http://localhost:8000/api/contact",
    json={
        "name": "Jane Smith",
        "email": "jane@example.com",
        "message": "Hello! This is a test message."
    }
)

if response.status_code == 201:
    data = response.json()
    print(f"Success! Submission ID: {data['submission_id']}")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

### JavaScript/Fetch

```javascript
const formData = {
    name: "Jane Smith",
    email: "jane@example.com",
    message: "Hello! This is a test message."
};

fetch('/api/contact', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Success!', data.submission_id);
    } else {
        console.error('Error:', data.message);
    }
})
.catch(error => console.error('Network error:', error));
```

### cURL

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "message": "Hello! This is a test message."
  }'
```

## Validation Details

### Name Field
- **Length:** 2-100 characters
- **Allowed characters:** Letters (a-z, A-Z), spaces, hyphens (-), apostrophes (')
- **Examples:**
  - ✅ "John Doe"
  - ✅ "Mary-Jane Watson"
  - ✅ "O'Brien"
  - ❌ "John123" (contains numbers)
  - ❌ "J" (too short)

### Email Field
- **Format:** Standard email format (user@domain.tld)
- **Examples:**
  - ✅ "user@example.com"
  - ✅ "user.name@example.co.uk"
  - ✅ "user+tag@example.com"
  - ❌ "notanemail"
  - ❌ "missing@domain"

### Message Field
- **Length:** 10-2000 characters
- **Whitespace:** Leading/trailing whitespace is trimmed
- **Examples:**
  - ✅ "This is a valid message with sufficient length."
  - ❌ "Too short" (less than 10 characters)
  - ❌ "          " (only whitespace)

## Error Handling

The application implements comprehensive error handling at multiple layers:

### Client-Side
- Real-time validation on field blur
- Visual feedback (error/success states)
- Character counter for message field
- Clear error messages for users
- Network error handling

### Server-Side
- Pydantic model validation
- Custom validators for complex rules
- HTTP exception handling
- Detailed error responses
- Logging of all errors

### Error Response Format

All error responses follow a consistent structure:

```json
{
  "success": false,
  "message": "Human-readable error message",
  "errors": {
    "field_name": ["Specific error message"]
  },
  "error_code": "ERROR_CODE"
}
```

**Error Codes:**
- `VALIDATION_ERROR`: Input validation failed
- `INTERNAL_ERROR`: Server error occurred
- `NETWORK_ERROR`: Client network error

## Testing

### Test Coverage

The test suite includes:

- **Model validation tests** (`test_models.py`):
  - Valid data acceptance
  - Invalid data rejection
  - Edge cases (min/max lengths, special characters)
  - Whitespace handling
  - Missing field detection

- **API integration tests** (`test_api.py`):
  - Successful form submission
  - Validation error handling
  - CORS configuration
  - Error response formats
  - Service layer testing

### Running Specific Tests

```bash
# Test models only
pytest contact_form/tests/test_models.py

# Test API only
pytest contact_form/tests/test_api.py

# Test specific test class
pytest contact_form/tests/test_models.py::TestContactFormRequest

# Test specific test method
pytest contact_form/tests/test_models.py::TestContactFormRequest::test_valid_contact_form
```

## Security Considerations

### Input Sanitization
- All input is validated and sanitized
- Regex patterns prevent injection attacks
- Length limits prevent DoS attacks
- Email validation prevents malformed addresses

### CORS Configuration
- Currently set to allow all origins (`*`) for development
- **Production:** Configure specific allowed origins

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

### Rate Limiting
Consider adding rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/contact")
@limiter.limit("5/minute")
async def submit_contact_form(...):
    ...
```

## Production Deployment

### Environment Variables

Create a `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Email Service (example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Database (example)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY contact_form/ ./contact_form/

CMD ["uvicorn", "contact_form.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t contact-form .
docker run -p 8000:8000 contact-form
```

### Integration with Email Services

Example integration with SendGrid:

```python
import sendgrid
from sendgrid.helpers.mail import Mail

async def send_email_notification(form_data: ContactFormRequest):
    message = Mail(
        from_email='noreply@yourdomain.com',
        to_emails='support@yourdomain.com',
        subject=f'New contact form submission from {form_data.name}',
        html_content=f'''
            <h2>New Contact Form Submission</h2>
            <p><strong>From:</strong> {form_data.name}</p>
            <p><strong>Email:</strong> {form_data.email}</p>
            <p><strong>Message:</strong></p>
            <p>{form_data.message}</p>
        '''
    )
    
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    return response
```

### Database Integration

Example with SQLAlchemy:

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ContactSubmission(Base):
    __tablename__ = 'contact_submissions'
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(String(12), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
async def save_submission(submission_id: str, form_data: ContactFormRequest):
    submission = ContactSubmission(
        submission_id=submission_id,
        name=form_data.name,
        email=form_data.email,
        message=form_data.message
    )
    db.add(submission)
    await db.commit()
```

## Customization

### Changing Validation Rules

Edit `models.py`:

```python
class ContactFormRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=3,  # Changed from 2
        max_length=150,  # Changed from 100
        description="Full name"
    )
```

### Customizing UI

Edit `static/contact_form.html` and `static/contact_form.js` to change:
- Colors and styling
- Field labels
- Validation messages
- Success/error messages

### Adding Fields

1. Update model in `models.py`:
```python
class ContactFormRequest(BaseModel):
    # ... existing fields ...
    phone: Optional[str] = Field(None, description="Phone number")
```

2. Update HTML form
3. Update JavaScript validation
4. Update tests

## License

This contact form implementation is provided as-is for use in your projects.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.
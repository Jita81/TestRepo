# Contact Form Implementation

A production-ready contact form with comprehensive security features, validation, and user experience enhancements.

## Features

### ✅ Core Requirements
- **Name Field**: Text input with validation (required, 2-100 characters)
- **Email Field**: Email input with comprehensive validation (required, valid format)
- **Submit Button**: Clear call-to-action labeled "Send Message"
- **Visual Feedback**: Real-time validation errors with animations
- **AJAX Submission**: Asynchronous form submission using Fetch API
- **Backend Validation**: Server-side input sanitization and validation
- **Success Handling**: Form clears and displays success message
- **Database Storage**: All submissions stored with timestamps

### 🔒 Security Features
- **CSRF Protection**: Token-based protection against cross-site request forgery
- **Input Sanitization**: HTML escaping to prevent XSS attacks
- **SQL Injection Prevention**: Parameterized queries with prepared statements
- **Rate Limiting**: IP-based rate limiting (5 requests per 15 minutes)
- **Input Length Limits**: Enforced on both client and server
- **Content Security**: Validation patterns prevent malicious input

### 📱 User Experience
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop
- **Real-time Validation**: Debounced validation as user types
- **Character Counters**: Live character count for both fields
- **Loading States**: Clear visual feedback during submission
- **Error Messages**: Specific, actionable error messages
- **Success Animations**: Smooth transitions and feedback
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Browser Autofill**: Proper autocomplete attributes

### 🎨 Design Features
- Modern gradient background
- Clean, card-based layout
- Smooth animations and transitions
- Focus states and visual feedback
- Mobile-first responsive design
- High contrast mode support
- Reduced motion support for accessibility

## File Structure

```
/workspace/
├── src/
│   ├── database.py              # Database models and operations
│   ├── contact_validation.py   # Input validation and sanitization
│   └── contact_routes.py        # API endpoints and routes
├── templates/
│   └── contact.html             # Contact form HTML template
├── static/
│   └── js/
│       └── contact-form.js      # Client-side form handling
├── tests/
│   └── test_contact_form.py     # Comprehensive test suite
└── contacts.db                  # SQLite database (auto-created)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The database will be automatically created on first run.

## Usage

### Start the Application

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

### Access the Contact Form

Navigate to: `http://localhost:8000/contact`

### API Endpoints

#### Get CSRF Token
```http
GET /api/csrf-token
```

Response:
```json
{
  "success": true,
  "csrf_token": "..."
}
```

#### Submit Contact Form
```http
POST /api/contact
Content-Type: application/x-www-form-urlencoded

fullName=John+Doe&email=john@example.com&csrf_token=...
```

Success Response (200):
```json
{
  "success": true,
  "message": "Thank you for your message! We'll be in touch soon.",
  "contact_id": 1,
  "remaining_requests": 4
}
```

Validation Error (400):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "fullName": "Full name is required",
    "email": "Invalid email format"
  }
}
```

Rate Limit Error (429):
```json
{
  "success": false,
  "message": "Too many requests. Please try again later.",
  "retry_after": 900
}
```

#### Get Contacts (Admin)
```http
GET /api/contacts?limit=100&offset=0
```

Response:
```json
{
  "success": true,
  "contacts": [
    {
      "id": 1,
      "full_name": "John Doe",
      "email": "john@example.com",
      "created_at": "2025-10-05 12:00:00",
      "ip_address": "127.0.0.1"
    }
  ],
  "count": 1
}
```

## Database Schema

### contacts Table
```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

### rate_limits Table
```sql
CREATE TABLE rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(45) NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address)
);
```

## Validation Rules

### Full Name
- **Required**: Yes
- **Min Length**: 2 characters
- **Max Length**: 100 characters
- **Pattern**: Letters, spaces, hyphens, apostrophes, and dots
- **Special Cases**: Unicode letters supported (José, María, etc.)
- **Blocked**: Consecutive numbers (3+), HTML tags

### Email
- **Required**: Yes
- **Max Length**: 254 characters
- **Format**: RFC 5322 compliant
- **Additional Checks**:
  - Must contain exactly one @ symbol
  - Local part max 64 characters
  - Domain must contain at least one dot
  - No consecutive dots (..)
- **Normalization**: Converted to lowercase

## Security Considerations

### CSRF Protection
- Tokens generated using `secrets.token_urlsafe(32)`
- Tokens validated server-side on each submission
- Tokens expire after 1 hour
- Used token is immediately invalidated

### Rate Limiting
- **Window**: 15 minutes (configurable)
- **Max Requests**: 5 per IP (configurable)
- **Implementation**: Database-backed with automatic cleanup
- **Tracking**: By IP address (supports proxy headers)

### Input Sanitization
- HTML special characters escaped
- Whitespace trimmed
- Length limits enforced
- Pattern matching for allowed characters
- XSS prevention through escaping

### SQL Injection Prevention
- All queries use parameterized statements
- No string concatenation in queries
- Connection pooling with proper cleanup
- Transaction support with rollback

## Testing

Run the complete test suite:

```bash
pytest tests/test_contact_form.py -v
```

### Test Coverage
- ✅ Input validation (valid and invalid cases)
- ✅ Email format validation
- ✅ Sanitization and XSS prevention
- ✅ Database operations (insert, retrieve, pagination)
- ✅ Rate limiting functionality
- ✅ CSRF token generation and validation
- ✅ API endpoint responses
- ✅ Error handling
- ✅ Special characters and Unicode
- ✅ SQL injection prevention

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Accessibility

- **ARIA Labels**: All form fields properly labeled
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Error messages announced via aria-live
- **Focus Management**: Clear focus indicators
- **High Contrast**: Supports high contrast mode
- **Reduced Motion**: Respects prefers-reduced-motion

## Performance

### Frontend
- Debounced validation (300ms delay)
- Minimal DOM manipulation
- CSS animations (GPU accelerated)
- Lazy validation on input

### Backend
- Connection pooling
- Indexed database queries
- Efficient rate limiting
- Minimal memory footprint

## Edge Cases Handled

✅ Multiple rapid form submissions (rate limiting)  
✅ Very long input values (length validation)  
✅ Special characters and Unicode (pattern matching)  
✅ Unusual email formats (comprehensive validation)  
✅ Browser auto-fill (proper autocomplete attributes)  
✅ Network timeout (error handling and retry)  
✅ Database connection failure (graceful error handling)  
✅ XSS attempts (input sanitization)  
✅ Different browser rendering (cross-browser CSS)  
✅ Form submission with JavaScript disabled (HTML5 validation fallback)

## Configuration

### Rate Limiting
Edit in `src/contact_routes.py`:
```python
is_allowed, remaining = db.check_rate_limit(
    client_ip,
    max_requests=5,        # Change this
    window_minutes=15      # Change this
)
```

### Database Path
Edit in `src/database.py`:
```python
_db_path = Path("contacts.db")  # Change this
```

### Validation Rules
Edit in `src/contact_validation.py`:
```python
MAX_NAME_LENGTH = 100  # Change this
MAX_EMAIL_LENGTH = 254 # Change this
```

## Production Deployment

### Recommendations

1. **CSRF Tokens**: Use Redis instead of in-memory storage
2. **Database**: Consider PostgreSQL for production
3. **Rate Limiting**: Use Redis for distributed rate limiting
4. **Logging**: Add proper logging for errors and submissions
5. **Monitoring**: Monitor submission rates and errors
6. **Email Notifications**: Send email notifications on new submissions
7. **Admin Dashboard**: Create admin interface to view submissions
8. **CAPTCHA**: Add reCAPTCHA for additional spam prevention
9. **HTTPS**: Ensure SSL/TLS is properly configured
10. **Environment Variables**: Use environment variables for configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis (for CSRF and rate limiting)
REDIS_URL=redis://localhost:6379

# Security
CSRF_SECRET_KEY=your-secret-key-here

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=15
```

## License

This implementation follows security best practices and is production-ready.

## Support

For issues or questions, please refer to the test suite for usage examples.
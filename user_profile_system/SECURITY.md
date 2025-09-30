# Security Documentation

## Overview

This document outlines the security measures implemented in the User Profile System to protect against common vulnerabilities and ensure data safety.

## Security Features

### 1. Authentication & Authorization

#### JWT-Based Authentication
- **Implementation**: JSON Web Tokens (JWT) for stateless authentication
- **Token Expiration**: 30 minutes (configurable)
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Storage**: LocalStorage (client-side)

**Security Considerations:**
- Tokens are signed with a secret key
- Tokens include expiration timestamp
- Invalid tokens result in 401 Unauthorized
- Expired tokens automatically trigger re-authentication

#### Password Security
- **Hashing Algorithm**: bcrypt
- **Salt Rounds**: Automatic (handled by passlib)
- **Password Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit

**Code Example:**
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)
```

#### Authorization
- Users can only edit their own profiles
- Authorization checks performed on every profile update
- User ID extracted from JWT token
- Ownership verification before modifications

### 2. Input Validation & Sanitization

#### Backend Validation (Pydantic)
All input is validated using Pydantic schemas:

```python
class UserProfileBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

#### Input Sanitization
- **Library**: Bleach (Python)
- **Purpose**: Remove dangerous HTML/JavaScript
- **Whitelist Approach**: Only allow safe tags and attributes

```python
def sanitize_input(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)
```

#### Frontend Validation
- Real-time validation on user input
- Type checking with TypeScript
- Format validation (email, name patterns)

#### Frontend Sanitization
- **Library**: DOMPurify
- **Applied**: Before displaying any user-generated content
- **Protection**: XSS attack prevention

```typescript
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(dirty);
```

### 3. XSS (Cross-Site Scripting) Prevention

#### Multiple Layers of Protection

1. **Input Sanitization**: All inputs cleaned before storage
2. **Output Encoding**: Data encoded before display
3. **Content Security Policy**: Recommended for production
4. **React's Default Protection**: JSX automatically escapes content

#### Vulnerable Areas Protected
- User names
- Email addresses
- Profile descriptions (if added)
- Any user-generated content

### 4. File Upload Security

#### Validation Layers

**Frontend Validation:**
```typescript
const validateImageFile = (file: File): string | null => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!allowedTypes.includes(file.type)) {
    return 'Invalid file type';
  }
  if (file.size > maxSize) {
    return 'File too large';
  }
  return null;
};
```

**Backend Validation:**
- MIME type checking
- File extension verification
- Size limits (5MB)
- Image verification (using Pillow)

**Image Processing:**
- Resize to maximum dimensions (800x800)
- Format conversion (RGBA → RGB)
- Optimization and compression
- Removal of EXIF data (privacy)

**Storage Security:**
- Unique filenames (UUID-based)
- Separate upload directory
- No execution permissions on upload folder
- Path traversal prevention

### 5. SQL Injection Prevention

#### ORM Protection
- **SQLAlchemy ORM**: Automatic query parameterization
- No raw SQL queries with user input
- Prepared statements for all queries

**Safe Example:**
```python
# Safe - uses ORM
user = db.query(User).filter(User.email == email).first()

# Dangerous (NOT used in our code)
# db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 6. CORS (Cross-Origin Resource Sharing)

#### Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Whitelist specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Recommendation:**
- Specify exact allowed origins
- Avoid wildcards (*)
- Enable credentials only if needed
- Restrict HTTP methods

### 7. Rate Limiting (Recommended for Production)

While not implemented in the current version, rate limiting should be added:

```python
# Recommended addition
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

### 8. HTTPS & Transport Security

**Production Requirements:**
- Use HTTPS for all communications
- HTTP Strict Transport Security (HSTS)
- Secure cookie flags
- TLS 1.2 or higher

**Headers to Add:**
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 9. Session Management

#### Token Storage
- Tokens stored in LocalStorage
- Cleared on logout
- Automatic cleanup on expiration

#### Session Timeout
- 30-minute token expiration
- Automatic redirect on expired session
- No sensitive data in client storage

**Improvement for Production:**
- Use HTTP-only cookies instead of LocalStorage
- Implement refresh token mechanism
- Add remember-me functionality with longer expiration

### 10. Error Handling

#### Security Considerations
- Generic error messages to users
- Detailed errors logged server-side
- No stack traces in production responses
- No sensitive information in error messages

**Example:**
```python
# Good - Generic message
raise HTTPException(status_code=401, detail="Invalid credentials")

# Bad - Too specific
# raise HTTPException(detail="User not found in database")
```

## Vulnerability Assessment

### Common Attacks - Mitigation Status

| Attack Type | Mitigation | Status |
|-------------|------------|--------|
| SQL Injection | ORM (SQLAlchemy) | ✅ Protected |
| XSS | Sanitization (Bleach, DOMPurify) | ✅ Protected |
| CSRF | JWT (stateless auth) | ✅ Protected |
| Password Attacks | bcrypt hashing, strong requirements | ✅ Protected |
| File Upload Attacks | Type/size validation, processing | ✅ Protected |
| Session Hijacking | JWT expiration, HTTPS | ⚠️ Partial (Add HTTPS in prod) |
| Brute Force | Password complexity | ⚠️ Partial (Add rate limiting) |
| MITM | HTTPS | ⚠️ Add in production |
| Directory Traversal | UUID filenames, path validation | ✅ Protected |
| Code Injection | Input sanitization, no eval() | ✅ Protected |

## Security Checklist for Production

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set strong SECRET_KEY (32+ random characters)
- [ ] Configure CORS with specific origins
- [ ] Add rate limiting to authentication endpoints
- [ ] Implement account lockout after failed attempts
- [ ] Add CAPTCHA to registration/login
- [ ] Enable security headers (CSP, HSTS, etc.)
- [ ] Use HTTP-only cookies instead of LocalStorage
- [ ] Implement refresh token mechanism
- [ ] Set up monitoring and alerting
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Implement logging for security events
- [ ] Add two-factor authentication (2FA)
- [ ] Database encryption at rest
- [ ] Regular backups with encryption
- [ ] Implement Content Security Policy
- [ ] Add subresource integrity (SRI) for CDN assets

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email security concerns to: [security@example.com]
3. Include detailed description and reproduction steps
4. Allow time for patching before public disclosure

## Security Updates

- Dependencies are regularly updated
- Security patches applied promptly
- Following semantic versioning
- Changelog includes security fixes

## Compliance Considerations

### GDPR Compliance
- User data can be exported
- User accounts can be deleted
- Data minimization principles
- Consent for data processing

### Data Protection
- Passwords are hashed (never stored plain)
- Personal data encrypted in transit
- Access control on all endpoints
- Audit logging recommended

## Best Practices for Developers

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Validate all input** on both client and server
4. **Sanitize all output** before displaying
5. **Keep dependencies updated** regularly
6. **Follow principle of least privilege**
7. **Log security events** for monitoring
8. **Test security features** thoroughly
9. **Review code for security issues**
10. **Stay informed** about new vulnerabilities

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security Best Practices](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
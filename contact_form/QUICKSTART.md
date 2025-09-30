# Quick Start Guide

Get the contact form up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation & Setup

### Step 1: Install Dependencies

```bash
# Option 1: Using pip directly (with virtual environment recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Using the minimal requirements
pip install fastapi uvicorn pydantic[email]
```

### Step 2: Start the Server

```bash
# From the contact_form directory
uvicorn api:app --reload

# Or from the parent directory
uvicorn contact_form.api:app --reload
```

The server will start at `http://localhost:8000`

### Step 3: Access the Contact Form

Open your browser and navigate to:

**Option 1: Static HTML File**
```
file:///path/to/contact_form/static/contact_form.html
```

**Option 2: Serve via Python HTTP Server**
```bash
cd static
python3 -m http.server 8080
```
Then open: `http://localhost:8080/contact_form.html`

**Option 3: Use the API Directly**

Visit the interactive API documentation:
```
http://localhost:8000/docs
```

## Testing the API

### Using the Interactive Docs

1. Go to `http://localhost:8000/docs`
2. Click on `POST /api/contact`
3. Click "Try it out"
4. Fill in the example data:
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "message": "Hello! This is a test message."
   }
   ```
5. Click "Execute"

### Using cURL

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello! This is a test message."
  }'
```

### Using Python

```bash
# Install httpx if not already installed
pip install httpx

# Run the example script
python3 example_usage.py
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
contact_form/
├── api.py                  # FastAPI application and endpoints
├── models.py               # Pydantic models and validation
├── static/
│   ├── contact_form.html   # Frontend UI
│   └── contact_form.js     # Client-side validation
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Model validation tests
│   └── test_api.py         # API integration tests
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── example_usage.py       # Usage examples
├── README.md              # Comprehensive documentation
└── QUICKSTART.md          # This file
```

## Common Issues

### Port Already in Use

If port 8000 is already in use:
```bash
uvicorn contact_form.api:app --reload --port 8001
```

### CORS Errors

If you're accessing the API from a different origin, update the CORS settings in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Import Errors

Make sure you're in the correct directory:
```bash
# If running from contact_form directory:
uvicorn api:app --reload

# If running from parent directory:
uvicorn contact_form.api:app --reload
```

## Next Steps

1. **Customize the Form**: Edit `static/contact_form.html` and `static/contact_form.js`
2. **Add Email Integration**: See README.md for SendGrid/SMTP examples
3. **Add Database Storage**: See README.md for SQLAlchemy examples
4. **Deploy to Production**: See README.md for Docker and deployment guides
5. **Add Rate Limiting**: Protect against spam and abuse

## Support

- Full Documentation: `README.md`
- API Documentation: `http://localhost:8000/docs` (when server is running)
- Example Code: `example_usage.py`

## Validation Rules Summary

| Field   | Min Length | Max Length | Special Rules                           |
|---------|-----------|------------|----------------------------------------|
| Name    | 2         | 100        | Letters, spaces, hyphens, apostrophes  |
| Email   | -         | -          | Valid email format                     |
| Message | 10        | 2000       | Any characters (whitespace trimmed)    |

Happy coding! 🚀
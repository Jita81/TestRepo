# Greeting API

A production-ready RESTful API that returns greeting messages in multiple languages with support for personalized greetings.

## Features

✨ **Multi-language Support** - English, Spanish, and French greetings  
🎯 **Personalized Greetings** - Optional name parameter for custom messages  
🛡️ **Security** - Rate limiting, input validation, and security headers  
🚀 **High Performance** - Response times under 200ms  
🌐 **CORS Enabled** - Ready for web client integration  
✅ **Fully Tested** - Comprehensive unit and integration tests  
📚 **Well Documented** - OpenAPI/Swagger documentation included  

## Quick Start

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd greeting-api

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start the server
npm start
```

The API will be running at `http://localhost:3000`

### Development Mode

```bash
# Run with auto-reload
npm run dev
```

## API Endpoints

### Get Greeting

**GET** `/api/greeting`

Returns a greeting message in the specified language.

#### Query Parameters

| Parameter | Type   | Required | Description                                      |
|-----------|--------|----------|--------------------------------------------------|
| `lang`    | string | No       | Language code (en, es, fr). Default: en          |
| `name`    | string | No       | Name for personalized greeting (1-50 characters) |

#### Examples

```bash
# Default English greeting
curl http://localhost:3000/api/greeting
# Response: {"message": "Hello!"}

# Personalized English greeting
curl http://localhost:3000/api/greeting?name=John
# Response: {"message": "Hello, John!"}

# Spanish greeting
curl http://localhost:3000/api/greeting?lang=es
# Response: {"message": "¡Hola!"}

# Personalized Spanish greeting
curl http://localhost:3000/api/greeting?lang=es&name=Juan
# Response: {"message": "¡Hola, Juan!"}

# French greeting
curl http://localhost:3000/api/greeting?lang=fr&name=Marie
# Response: {"message": "Bonjour, Marie!"}
```

#### Response Codes

| Code | Description                           |
|------|---------------------------------------|
| 200  | Success                               |
| 400  | Bad Request (invalid parameters)      |
| 429  | Too Many Requests (rate limit)        |
| 500  | Internal Server Error                 |

### Get Supported Languages

**GET** `/api/greeting/languages`

Returns a list of all supported language codes.

```bash
curl http://localhost:3000/api/greeting/languages
# Response: {"languages": ["en", "es", "fr"], "count": 3}
```

### Health Check

**GET** `/health`

Returns the health status of the API.

```bash
curl http://localhost:3000/health
# Response: {"status": "healthy", "timestamp": "2025-09-30T12:00:00.000Z", "uptime": 123.45}
```

## Supported Languages

| Code | Language | Default Greeting | With Name           |
|------|----------|------------------|---------------------|
| en   | English  | Hello!           | Hello, {name}!      |
| es   | Spanish  | ¡Hola!           | ¡Hola, {name}!      |
| fr   | French   | Bonjour!         | Bonjour, {name}!    |

## Input Validation

### Name Parameter

- **Length**: 1-50 characters
- **Allowed Characters**: Letters (including Unicode), spaces, hyphens, apostrophes
- **Examples**: 
  - ✅ Valid: `John`, `Mary-Jane`, `O'Brien`, `José`, `María-José`
  - ❌ Invalid: `John123`, `John@Doe`, `<script>`

### Language Parameter

- **Format**: Exactly 2 characters
- **Case**: Insensitive (automatically converted to lowercase)
- **Supported**: `en`, `es`, `fr`

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Window**: 15 minutes
- **Max Requests**: 100 per IP address
- **Headers**: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`

When rate limit is exceeded:
- Status Code: `429 Too Many Requests`
- Response includes `Retry-After` header

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "message": "Error description",
    "status": 400,
    "timestamp": "2025-09-30T12:00:00.000Z",
    "details": [
      {
        "field": "name",
        "message": "Validation error message",
        "value": "invalid-value"
      }
    ]
  }
}
```

## Security Features

- **Helmet**: Security headers (XSS protection, content type options, etc.)
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: IP-based request throttling
- **Input Validation**: Strict validation with express-validator
- **Error Handling**: No stack traces exposed in production

## Testing

### Run All Tests

```bash
npm test
```

### Run Unit Tests Only

```bash
npm run test:unit
```

### Run Integration Tests Only

```bash
npm run test:integration
```

### Watch Mode

```bash
npm run test:watch
```

### Test Coverage

The project includes comprehensive test coverage:

- ✅ Unit tests for business logic
- ✅ Integration tests for API endpoints
- ✅ Edge case handling
- ✅ Error scenarios
- ✅ Performance tests (response time < 200ms)

Run `npm test` to generate a coverage report in the `coverage/` directory.

## Project Structure

```
greeting-api/
├── src/
│   ├── app.js                  # Express application setup
│   ├── server.js               # Server entry point
│   ├── config/
│   │   └── index.js            # Configuration management
│   ├── middleware/
│   │   ├── errorHandler.js     # Error handling middleware
│   │   ├── rateLimiter.js      # Rate limiting middleware
│   │   └── validator.js        # Request validation middleware
│   ├── routes/
│   │   └── greeting.js         # Greeting routes
│   ├── services/
│   │   └── greetingService.js  # Business logic
│   └── utils/
│       └── constants.js        # Constants and configuration
├── tests/
│   ├── unit/                   # Unit tests
│   │   └── greetingService.test.js
│   └── integration/            # Integration tests
│       └── greeting.test.js
├── docs/
│   └── swagger.yaml            # OpenAPI documentation
├── .env                        # Environment variables
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
├── package.json                # Dependencies and scripts
└── README.md                   # This file
```

## Configuration

Environment variables can be configured in the `.env` file:

```env
PORT=3000                       # Server port
NODE_ENV=development            # Environment (development/production)
RATE_LIMIT_WINDOW=15            # Rate limit window in minutes
RATE_LIMIT_MAX_REQUESTS=100     # Max requests per window
```

## API Documentation

Full OpenAPI 3.0 documentation is available at `docs/swagger.yaml`.

You can view the documentation using:
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Swagger Editor](https://editor.swagger.io/)
- [Redoc](https://redocly.github.io/redoc/)

## Performance

- ⚡ Response time: < 200ms (tested)
- 📊 Stateless design for horizontal scaling
- 🔄 Efficient string operations
- 💾 Minimal memory footprint

## Production Deployment

### Best Practices

1. **Environment Variables**: Use production values
2. **CORS**: Configure specific allowed origins
3. **Logging**: Implement proper logging (e.g., Winston, Bunyan)
4. **Monitoring**: Add APM tools (e.g., New Relic, DataDog)
5. **Process Manager**: Use PM2 or similar for process management
6. **HTTPS**: Always use HTTPS in production
7. **Rate Limiting**: Adjust limits based on your needs

### Example PM2 Configuration

```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start src/server.js --name greeting-api

# Enable auto-restart on file changes (development)
pm2 start src/server.js --name greeting-api --watch

# View logs
pm2 logs greeting-api

# Monitor
pm2 monit
```

## Edge Cases Handled

✅ Empty name parameter  
✅ Special characters in name (Unicode, hyphens, apostrophes)  
✅ Very long name parameters (truncated to 50 characters)  
✅ Invalid language codes  
✅ Multiple concurrent requests  
✅ Missing query parameters  
✅ Case sensitivity in language codes (normalized to lowercase)  
✅ Unicode character support in names  
✅ Rate limit exceeded scenarios  
✅ Whitespace normalization (leading, trailing, multiple spaces)  

## Dependencies

### Production

- `express` - Web framework
- `express-validator` - Request validation
- `express-rate-limit` - Rate limiting
- `cors` - CORS middleware
- `helmet` - Security headers
- `dotenv` - Environment variable management

### Development

- `jest` - Testing framework
- `supertest` - HTTP assertions
- `nodemon` - Development auto-reload

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT

## Support

For issues and questions, please open an issue in the repository.

---

**Made with ❤️ using Node.js and Express**
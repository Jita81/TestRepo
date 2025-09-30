# API Usage Examples

This document provides comprehensive examples of using the Greeting API.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Language Support](#language-support)
- [Personalized Greetings](#personalized-greetings)
- [Error Handling](#error-handling)
- [Edge Cases](#edge-cases)
- [Rate Limiting](#rate-limiting)

## Basic Usage

### Default Greeting (English)

```bash
curl http://localhost:3000/api/greeting
```

**Response:**
```json
{
  "message": "Hello!"
}
```

### Explicit Language

```bash
curl http://localhost:3000/api/greeting?lang=en
```

**Response:**
```json
{
  "message": "Hello!"
}
```

## Language Support

### Spanish Greeting

```bash
curl http://localhost:3000/api/greeting?lang=es
```

**Response:**
```json
{
  "message": "¡Hola!"
}
```

### French Greeting

```bash
curl http://localhost:3000/api/greeting?lang=fr
```

**Response:**
```json
{
  "message": "Bonjour!"
}
```

### Case Insensitive Language Codes

```bash
curl http://localhost:3000/api/greeting?lang=ES
curl http://localhost:3000/api/greeting?lang=Es
curl http://localhost:3000/api/greeting?lang=eS
```

All return:
```json
{
  "message": "¡Hola!"
}
```

## Personalized Greetings

### English with Name

```bash
curl http://localhost:3000/api/greeting?name=John
```

**Response:**
```json
{
  "message": "Hello, John!"
}
```

### Spanish with Name

```bash
curl http://localhost:3000/api/greeting?lang=es&name=Juan
```

**Response:**
```json
{
  "message": "¡Hola, Juan!"
}
```

### French with Name

```bash
curl http://localhost:3000/api/greeting?lang=fr&name=Marie
```

**Response:**
```json
{
  "message": "Bonjour, Marie!"
}
```

## Error Handling

### Invalid Language Code

```bash
curl http://localhost:3000/api/greeting?lang=xx
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [
      {
        "field": "lang",
        "message": "Unsupported language code. Supported languages: en, es, fr",
        "value": "xx"
      }
    ]
  }
}
```

### Invalid Language Code Length

```bash
curl http://localhost:3000/api/greeting?lang=eng
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [
      {
        "field": "lang",
        "message": "Language code must be exactly 2 characters",
        "value": "eng"
      }
    ]
  }
}
```

### Invalid Name Characters

```bash
curl http://localhost:3000/api/greeting?name=John123
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name can only contain letters, spaces, hyphens, and apostrophes",
        "value": "John123"
      }
    ]
  }
}
```

### Name with Special Symbols

```bash
curl http://localhost:3000/api/greeting?name=John@Doe
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name can only contain letters, spaces, hyphens, and apostrophes",
        "value": "John@Doe"
      }
    ]
  }
}
```

## Edge Cases

### Names with Hyphens

```bash
curl http://localhost:3000/api/greeting?name=Mary-Jane
```

**Response:**
```json
{
  "message": "Hello, Mary-Jane!"
}
```

### Names with Apostrophes

```bash
curl "http://localhost:3000/api/greeting?name=O'Brien"
```

**Response:**
```json
{
  "message": "Hello, O'Brien!"
}
```

### Unicode Characters

```bash
curl http://localhost:3000/api/greeting?name=María
```

**Response:**
```json
{
  "message": "Hello, María!"
}
```

### Complex Unicode Names

```bash
curl http://localhost:3000/api/greeting?lang=es&name=José-María
```

**Response:**
```json
{
  "message": "¡Hola, José-María!"
}
```

### Multiple Spaces (Normalized)

```bash
curl "http://localhost:3000/api/greeting?name=John   Doe"
```

**Response:**
```json
{
  "message": "Hello, John Doe!"
}
```

### Leading/Trailing Whitespace (Trimmed)

```bash
curl "http://localhost:3000/api/greeting?name=  John  "
```

**Response:**
```json
{
  "message": "Hello, John!"
}
```

### Very Long Names (Truncated)

```bash
curl "http://localhost:3000/api/greeting?name=$(printf 'A%.0s' {1..100})"
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name must be between 1 and 50 characters",
        "value": "AAAA..."
      }
    ]
  }
}
```

## Rate Limiting

### Check Rate Limit Headers

```bash
curl -i http://localhost:3000/api/greeting
```

**Response Headers:**
```
HTTP/1.1 200 OK
RateLimit-Limit: 100
RateLimit-Remaining: 99
RateLimit-Reset: 1609459200
Content-Type: application/json
```

### Rate Limit Exceeded

After 100 requests within 15 minutes:

```bash
curl http://localhost:3000/api/greeting
```

**Response (429 Too Many Requests):**
```json
{
  "error": {
    "message": "Too many requests from this IP, please try again later.",
    "status": 429,
    "retryAfter": 900
  }
}
```

**Response Headers:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 900
```

## Utility Endpoints

### Get Supported Languages

```bash
curl http://localhost:3000/api/greeting/languages
```

**Response:**
```json
{
  "languages": ["en", "es", "fr"],
  "count": 3
}
```

### Health Check

```bash
curl http://localhost:3000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-30T12:00:00.000Z",
  "uptime": 123.45
}
```

## JavaScript/Node.js Examples

### Using Fetch API

```javascript
// Default greeting
const response = await fetch('http://localhost:3000/api/greeting');
const data = await response.json();
console.log(data.message); // "Hello!"

// Personalized Spanish greeting
const response2 = await fetch('http://localhost:3000/api/greeting?lang=es&name=Juan');
const data2 = await response2.json();
console.log(data2.message); // "¡Hola, Juan!"
```

### Using Axios

```javascript
const axios = require('axios');

// Default greeting
const { data } = await axios.get('http://localhost:3000/api/greeting');
console.log(data.message); // "Hello!"

// With parameters
const { data: data2 } = await axios.get('http://localhost:3000/api/greeting', {
  params: { lang: 'fr', name: 'Marie' }
});
console.log(data2.message); // "Bonjour, Marie!"
```

## Python Examples

### Using Requests Library

```python
import requests

# Default greeting
response = requests.get('http://localhost:3000/api/greeting')
print(response.json()['message'])  # "Hello!"

# Personalized greeting
params = {'lang': 'es', 'name': 'Juan'}
response = requests.get('http://localhost:3000/api/greeting', params=params)
print(response.json()['message'])  # "¡Hola, Juan!"

# Check rate limit headers
print(response.headers['RateLimit-Remaining'])
```

## Summary

- All endpoints return JSON
- Default language is English (`en`)
- Names support Unicode characters
- Language codes are case-insensitive
- Rate limiting applies to all endpoints
- Comprehensive validation ensures data quality
- CORS enabled for web client integration
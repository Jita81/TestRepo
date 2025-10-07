# Comprehensive Logging System Documentation

## Overview

The GitHub to App Converter includes a comprehensive logging system with structured logs, log rotation, and multiple output formats. This document explains how to use and configure the logging system.

## Features

### 1. **Structured JSON Logging**
- Logs are output in JSON format for easy parsing and analysis
- Each log entry includes timestamp, level, logger name, message, and context
- Perfect for log aggregation tools (ELK Stack, Splunk, etc.)

### 2. **Log Rotation**
- Automatic log file rotation based on file size
- Configurable maximum file size (default: 10MB)
- Keeps a configurable number of backup files (default: 5)

### 3. **Multiple Log Handlers**
- **Console output**: Human-readable with colors (or JSON)
- **Application log**: All logs (INFO and above)
- **Error log**: Only ERROR and CRITICAL logs
- **Access log**: HTTP request/response logs

### 4. **Context-Aware Logging**
- Request tracking with unique request IDs
- Thread and process information
- Stack traces for errors

### 5. **Multiple Log Levels**
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

## Log File Structure

```
logs/
├── github_to_app.log           # All application logs
├── github_to_app.log.1         # Rotated backup
├── github_to_app.log.2         # Rotated backup
├── github_to_app_error.log     # Error-only logs
├── github_to_app_error.log.1   # Rotated backup
├── github_to_app_access.log    # HTTP access logs
└── github_to_app_access.log.1  # Rotated backup
```

## Usage

### Basic Usage

The logging system is automatically initialized when the application starts. Simply import and use the logger:

```python
from src.logger_config import get_logger

logger = get_logger(__name__)

# Log messages
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical error!")
```

### Logging with Extra Context

Add extra context to your log entries:

```python
logger.info(
    "Processing repository",
    extra={
        "repo_url": "https://github.com/user/repo",
        "app_name": "my_app",
        "platform": "docker"
    }
)
```

This will add the extra fields to the JSON log output.

### Request Context Tracking

For HTTP requests, context is automatically tracked:

```python
from src.logger_config import set_request_context, clear_request_context

# Set context for the current request
set_request_context(
    request_id="unique-id",
    user_id="user123",
    operation="convert_repo"
)

# Your code here...

# Clear context when done
clear_request_context()
```

## Configuration

### Environment-Based Configuration

Configure logging when setting up the application:

```python
from src.logger_config import setup_logging

setup_logging(
    app_name="github_to_app",
    log_dir="logs",
    log_level="INFO",           # or "DEBUG", "WARNING", "ERROR", "CRITICAL"
    console_output=True,
    file_output=True,
    json_format=True,           # JSON format for file logs
    max_bytes=10 * 1024 * 1024, # 10MB per log file
    backup_count=5,             # Keep 5 backup files
    structured_console=False    # Human-readable console output
)
```

### YAML Configuration File

You can also use the `logging_config.yaml` file to configure logging:

```yaml
app_name: github_to_app
log_dir: logs
log_level: INFO

console_output:
  enabled: true
  json_format: false

file_output:
  enabled: true
  json_format: true

rotation:
  max_bytes: 10485760
  backup_count: 5
```

## Log Format Examples

### Console Output (Human-Readable)

```
[2025-10-07 12:34:56] [INFO] [main] Application started
[2025-10-07 12:34:57] [DEBUG] [github_integration] Cloning repository
[2025-10-07 12:34:58] [ERROR] [agentic_coder] AI analysis failed (main.py:123)
```

### JSON Log Output

```json
{
  "timestamp": "2025-10-07T12:34:56.789Z",
  "level": "INFO",
  "logger": "main",
  "message": "Starting conversion for repository",
  "module": "main",
  "function": "convert_repository",
  "line": 145,
  "process": 12345,
  "thread": 67890,
  "thread_name": "MainThread",
  "context": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "method": "POST",
    "url": "http://localhost:8000/convert"
  },
  "extra": {
    "github_url": "https://github.com/user/repo",
    "app_name": "my_app",
    "target_platform": "docker"
  }
}
```

### Error Log with Exception

```json
{
  "timestamp": "2025-10-07T12:35:00.123Z",
  "level": "ERROR",
  "logger": "agentic_coder",
  "message": "AI analysis failed",
  "module": "agentic_coder",
  "function": "analyze_codebase",
  "line": 75,
  "process": 12345,
  "thread": 67890,
  "thread_name": "MainThread",
  "exception": {
    "type": "OpenAIError",
    "message": "API request timeout",
    "traceback": "Traceback (most recent call last):\n  File ..."
  },
  "stack_trace": "..."
}
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Use for detailed debugging information
  ```python
  logger.debug(f"Processing file: {filename}")
  ```

- **INFO**: Use for general informational messages
  ```python
  logger.info("Repository cloned successfully")
  ```

- **WARNING**: Use for potentially problematic situations
  ```python
  logger.warning("No README file found, using defaults")
  ```

- **ERROR**: Use for errors that prevent specific operations
  ```python
  logger.error("Failed to parse dependencies", exc_info=True)
  ```

- **CRITICAL**: Use for critical errors that may stop the application
  ```python
  logger.critical("Database connection lost")
  ```

### 2. Include Exception Information

Always include `exc_info=True` when logging exceptions:

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={"operation": "risky"})
    raise
```

### 3. Add Contextual Information

Use the `extra` parameter to add context:

```python
logger.info(
    "Task completed",
    extra={
        "task_id": task_id,
        "duration_ms": duration,
        "result": "success"
    }
)
```

### 4. Use Named Loggers

Always use module-specific loggers:

```python
logger = get_logger(__name__)  # Uses module name as logger name
```

### 5. Avoid Logging Sensitive Information

Never log passwords, API keys, or other sensitive data:

```python
# BAD
logger.info(f"User logged in with password: {password}")

# GOOD
logger.info(f"User logged in", extra={"user_id": user_id})
```

## Log Analysis

### Using `jq` for JSON Logs

Filter and analyze JSON logs:

```bash
# Show only ERROR logs
cat logs/github_to_app.log | jq 'select(.level == "ERROR")'

# Show logs from specific module
cat logs/github_to_app.log | jq 'select(.logger == "agentic_coder")'

# Show logs with specific request ID
cat logs/github_to_app.log | jq 'select(.context.request_id == "550e8400...")'

# Count errors by type
cat logs/github_to_app.log | jq -r 'select(.level == "ERROR") | .exception.type' | sort | uniq -c
```

### Using grep for Quick Searches

```bash
# Find all ERROR logs
grep '"level": "ERROR"' logs/github_to_app.log

# Find logs mentioning a specific repository
grep 'github.com/user/repo' logs/github_to_app.log

# Find logs from last hour
grep "$(date -u +%Y-%m-%dT%H)" logs/github_to_app.log
```

## Monitoring and Alerts

### Integration with Log Aggregation Tools

The JSON log format is compatible with:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **New Relic**
- **Grafana Loki**

Example Logstash configuration:

```ruby
input {
  file {
    path => "/path/to/logs/github_to_app.log"
    codec => json
  }
}

filter {
  # Add custom filters here
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "github-to-app-%{+YYYY.MM.dd}"
  }
}
```

## Troubleshooting

### Logs Not Appearing

1. Check that the `logs` directory exists and is writable
2. Verify log level is set appropriately (DEBUG vs INFO)
3. Check console for any logging initialization errors

### Log Files Too Large

Adjust rotation settings:

```python
setup_logging(
    max_bytes=5 * 1024 * 1024,  # Reduce to 5MB
    backup_count=10              # Keep more backups
)
```

### Performance Issues

If logging impacts performance:

1. Increase log level to WARNING or ERROR
2. Disable file logging: `file_output=False`
3. Disable JSON formatting: `json_format=False`
4. Use asynchronous logging (advanced)

## Advanced Features

### Custom Log Handlers

Add custom log handlers:

```python
from src.logger_config import setup_logging

# Setup basic logging
config = setup_logging()

# Add custom handler (e.g., for specific module)
custom_handler = config.add_file_handler(
    name="custom_module",
    level=logging.DEBUG,
    max_bytes=1024*1024,
    backup_count=3
)
```

### Filtering Logs

Create custom filters:

```python
import logging

class CustomFilter(logging.Filter):
    def filter(self, record):
        # Only log records that meet certain criteria
        return 'important' in record.getMessage().lower()

logger.addFilter(CustomFilter())
```

## Summary

The comprehensive logging system provides:

- ✅ Structured JSON logs for easy parsing
- ✅ Automatic log rotation to prevent disk space issues
- ✅ Multiple log levels for different severity
- ✅ Context tracking for request correlation
- ✅ Multiple output handlers (console, file, error, access)
- ✅ Integration with log aggregation tools
- ✅ Configurable and extensible

For questions or issues, refer to the source code in `src/logger_config.py`.
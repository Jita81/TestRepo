# Logging System - Quick Start Guide

## ✅ Implementation Complete

A comprehensive logging system with structured logs and log rotation has been successfully added to your project!

## 📁 What Was Added

### Core Files
- **`src/logger_config.py`** - Main logging configuration module
- **`logging_config.yaml`** - Configuration example
- **`example_logging.py`** - Executable usage examples
- **`.gitignore`** - Prevents logs from being committed

### Documentation
- **`LOGGING.md`** - Complete documentation (9.7KB)
- **`LOGGING_IMPLEMENTATION_SUMMARY.md`** - Implementation details (11KB)
- **`LOGGING_QUICK_START.md`** - This file

### Updated Files
- ✅ `main.py` - HTTP request logging, startup/shutdown
- ✅ `run.py` - Startup sequence logging
- ✅ `src/agentic_coder.py` - AI operations logging
- ✅ `src/app_generator.py` - App generation logging
- ✅ `src/github_integration.py` - Repository operations logging
- ✅ `src/readme_parser.py` - README parsing logging
- ✅ `requirements.txt` - Added `python-json-logger`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Examples
```bash
# See logging in action
python example_logging.py

# Check created logs
ls -lh logs/
```

### 3. Start Your Application
```bash
python run.py
# or
python main.py
```

## 📊 Log Files

The system creates three log files automatically in the `logs/` directory:

1. **`github_to_app.log`** - All application logs (INFO+)
2. **`github_to_app_error.log`** - Errors only (ERROR+)
3. **`github_to_app_access.log`** - HTTP access logs

## 💡 Basic Usage

```python
from src.logger_config import get_logger

# Get a logger
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical issue!")

# Add extra context
logger.info(
    "Processing task",
    extra={
        "task_id": "123",
        "user": "john"
    }
)
```

## 🔍 View Logs

### Human-Readable Console
Logs appear in the console with colors when you run the app.

### JSON Log Files
View structured logs:
```bash
# Pretty print JSON logs
cat logs/github_to_app.log | jq

# Filter by log level
cat logs/github_to_app.log | jq 'select(.level == "ERROR")'

# Search by message
grep "repository" logs/github_to_app.log | jq
```

## ⚙️ Configuration

Edit settings in your code:
```python
from src.logger_config import setup_logging

setup_logging(
    app_name="github_to_app",
    log_dir="logs",
    log_level="INFO",        # DEBUG, INFO, WARNING, ERROR, CRITICAL
    console_output=True,
    file_output=True,
    json_format=True,
    max_bytes=10*1024*1024,  # 10MB per log file
    backup_count=5           # Keep 5 backup files
)
```

## 🎯 Key Features

✅ **Structured JSON logs** - Easy to parse and analyze  
✅ **Automatic log rotation** - Prevents disk space issues  
✅ **Multiple log levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL  
✅ **Request tracking** - Unique IDs for request correlation  
✅ **Exception handling** - Full stack traces captured  
✅ **Multiple handlers** - Console, file, error, access logs  
✅ **Context tracking** - Add custom context to logs  
✅ **Performance optimized** - Minimal overhead  

## 📖 Learn More

- **Full Documentation**: See `LOGGING.md`
- **Implementation Details**: See `LOGGING_IMPLEMENTATION_SUMMARY.md`
- **Examples**: Run `python example_logging.py`

## 🔧 Common Tasks

### Change Log Level
```python
setup_logging(log_level="DEBUG")  # More verbose
setup_logging(log_level="WARNING")  # Less verbose
```

### Disable File Logging
```python
setup_logging(file_output=False)
```

### Disable Console Logging
```python
setup_logging(console_output=False)
```

### Clean Up Old Logs
```bash
# Remove logs older than 30 days
find logs/ -name "*.log.*" -mtime +30 -delete
```

## 🎉 That's It!

Your logging system is ready to use. Every part of your application now has comprehensive logging with:
- Detailed operation tracking
- Error handling and debugging
- Performance monitoring
- Request correlation
- Structured output for analysis

Happy logging! 🚀

---

For questions or detailed information, see **LOGGING.md**
#!/usr/bin/env python3
"""
Example script demonstrating the comprehensive logging system.
Run this to see how the logging works.
"""

from src.logger_config import setup_logging, get_logger, set_request_context, clear_request_context
import time
import uuid

# Setup logging
print("Setting up logging system...")
setup_logging(
    app_name="logging_example",
    log_dir="logs",
    log_level="DEBUG",
    console_output=True,
    file_output=True,
    json_format=True
)

# Get logger
logger = get_logger(__name__)

def example_basic_logging():
    """Demonstrate basic logging levels."""
    print("\n=== Example 1: Basic Logging Levels ===")
    
    logger.debug("This is a DEBUG message - detailed information")
    logger.info("This is an INFO message - general information")
    logger.warning("This is a WARNING message - something to watch")
    logger.error("This is an ERROR message - something went wrong")
    logger.critical("This is a CRITICAL message - serious problem")

def example_logging_with_context():
    """Demonstrate logging with extra context."""
    print("\n=== Example 2: Logging with Extra Context ===")
    
    logger.info(
        "Processing user request",
        extra={
            "user_id": "user123",
            "operation": "convert_repository",
            "github_url": "https://github.com/example/repo"
        }
    )
    
    logger.info(
        "Task completed successfully",
        extra={
            "task_id": "task_456",
            "duration_seconds": 12.34,
            "items_processed": 42
        }
    )

def example_request_context():
    """Demonstrate request context tracking."""
    print("\n=== Example 3: Request Context Tracking ===")
    
    request_id = str(uuid.uuid4())
    
    # Set request context
    set_request_context(
        request_id=request_id,
        method="POST",
        url="/api/convert",
        user_id="user789"
    )
    
    logger.info("Request received")
    logger.debug("Processing request step 1")
    logger.debug("Processing request step 2")
    logger.info("Request completed successfully")
    
    # Clear context
    clear_request_context()

def example_exception_logging():
    """Demonstrate exception logging."""
    print("\n=== Example 4: Exception Logging ===")
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(
            "Mathematical error occurred",
            exc_info=True,
            extra={
                "operation": "division",
                "numerator": 10,
                "denominator": 0
            }
        )

def example_structured_operations():
    """Demonstrate logging in a structured operation."""
    print("\n=== Example 5: Structured Operation Logging ===")
    
    operation_id = str(uuid.uuid4())
    
    logger.info(
        "Starting repository clone operation",
        extra={
            "operation_id": operation_id,
            "repo_url": "https://github.com/example/demo"
        }
    )
    
    # Simulate work
    time.sleep(0.5)
    
    logger.debug(
        "Cloning in progress",
        extra={
            "operation_id": operation_id,
            "progress": 50
        }
    )
    
    time.sleep(0.5)
    
    logger.info(
        "Repository cloned successfully",
        extra={
            "operation_id": operation_id,
            "repo_size_mb": 15.3,
            "file_count": 234
        }
    )

def example_performance_logging():
    """Demonstrate performance logging."""
    print("\n=== Example 6: Performance Logging ===")
    
    start_time = time.time()
    
    # Simulate work
    time.sleep(1)
    
    duration = time.time() - start_time
    
    logger.info(
        "Operation completed",
        extra={
            "operation": "ai_analysis",
            "duration_seconds": round(duration, 3),
            "tokens_used": 1500,
            "cost_usd": 0.045
        }
    )

def example_conditional_logging():
    """Demonstrate conditional logging."""
    print("\n=== Example 7: Conditional Logging ===")
    
    results = {
        "success": True,
        "items_processed": 100,
        "errors": 2,
        "warnings": 5
    }
    
    if results["success"]:
        logger.info(
            "Batch processing completed",
            extra={
                "total_items": results["items_processed"],
                "errors": results["errors"],
                "warnings": results["warnings"]
            }
        )
    else:
        logger.error(
            "Batch processing failed",
            extra=results
        )
    
    # Log warnings if any
    if results["warnings"] > 0:
        logger.warning(
            f"Processing completed with {results['warnings']} warnings",
            extra={"warning_count": results["warnings"]}
        )

def main():
    """Run all examples."""
    print("=" * 60)
    print("Comprehensive Logging System Examples")
    print("=" * 60)
    
    logger.info("Starting logging examples")
    
    # Run examples
    example_basic_logging()
    example_logging_with_context()
    example_request_context()
    example_exception_logging()
    example_structured_operations()
    example_performance_logging()
    example_conditional_logging()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nCheck the following log files:")
    print("  - logs/logging_example.log (all logs)")
    print("  - logs/logging_example_error.log (errors only)")
    print("\nTip: Use 'cat logs/logging_example.log | jq' to view JSON logs")
    print("=" * 60)
    
    logger.info("All logging examples completed")

if __name__ == "__main__":
    main()
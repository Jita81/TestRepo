"""
Contact Form API Endpoints

This module implements the FastAPI endpoints for the contact form,
including comprehensive error handling and validation.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import uuid
from datetime import datetime
import logging
from typing import Union

from .models import ContactFormRequest, ContactFormResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Contact Form API",
    description="API for handling contact form submissions with validation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactFormService:
    """
    Service class for handling contact form submissions.
    
    In a production environment, this would integrate with:
    - Email service (SendGrid, SES, etc.)
    - Database for storing submissions
    - Queue system for async processing
    """
    
    @staticmethod
    async def process_submission(data: ContactFormRequest) -> ContactFormResponse:
        """
        Process a contact form submission.
        
        Args:
            data: Validated contact form data
            
        Returns:
            ContactFormResponse: Response with submission details
            
        Raises:
            HTTPException: If processing fails
        """
        try:
            # Generate unique submission ID
            submission_id = str(uuid.uuid4())[:12]
            
            # Log the submission (in production, this would save to database)
            logger.info(
                f"Contact form submission received - "
                f"ID: {submission_id}, "
                f"Name: {data.name}, "
                f"Email: {data.email}"
            )
            
            # Simulate email sending or other processing
            # In production, this might be:
            # await send_email(to=data.email, subject="...", body="...")
            # await save_to_database(submission_id, data)
            
            return ContactFormResponse(
                submission_id=submission_id,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error processing contact form: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your submission"
            )


@app.post(
    "/api/contact",
    response_model=ContactFormResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Contact form submitted successfully",
            "model": ContactFormResponse
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid request data",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    summary="Submit contact form",
    description="Submit a contact form with name, email, and message"
)
async def submit_contact_form(
    form_data: ContactFormRequest
) -> Union[ContactFormResponse, JSONResponse]:
    """
    Handle contact form submission.
    
    This endpoint validates the input data and processes the contact form submission.
    
    Args:
        form_data: Contact form data (name, email, message)
        
    Returns:
        ContactFormResponse: Success response with submission ID
        
    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        # Process the submission
        service = ContactFormService()
        response = await service.process_submission(form_data)
        
        logger.info(f"Contact form processed successfully: {response.submission_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
        
    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.warning(f"Validation error in contact form: {e.errors()}")
        error_response = ErrorResponse(
            message="Invalid input data",
            errors={err['loc'][-1]: [err['msg']] for err in e.errors()},
            error_code="VALIDATION_ERROR"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict()
        )
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in contact form: {str(e)}", exc_info=True)
        error_response = ErrorResponse(
            message="An unexpected error occurred. Please try again later.",
            error_code="INTERNAL_ERROR"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict()
        )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: API information
    """
    return {
        "name": "Contact Form API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "/api/contact",
            "health": "/api/health",
            "docs": "/docs"
        }
    }
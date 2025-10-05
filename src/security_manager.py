"""
Secure token and secrets management
Provides encryption and secure handling of sensitive data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages secure storage and retrieval of secrets."""
    
    def __init__(self):
        self.cipher_suite = self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Initialize encryption cipher from secure key."""
        # Get or generate encryption key
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not encryption_key:
            # Generate from system entropy if not provided
            logger.warning("No ENCRYPTION_KEY found, generating from system data")
            # Use a combination of environment-specific data
            seed = f"{os.getpid()}-{os.path.abspath('.')}"
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ecommerce-salt-change-in-production',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(seed.encode()))
        else:
            key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        
        return Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token securely."""
        if not token:
            return ""
        
        try:
            encrypted = self.cipher_suite.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt token: {e}")
            raise
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token."""
        if not encrypted_token:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            return ""
    
    def get_secure_token(self, token_name: str) -> str:
        """
        Retrieve token securely from environment or secure storage.
        
        Priority:
        1. AWS Secrets Manager (if configured)
        2. Environment variable (encrypted)
        3. Environment variable (plain - dev only)
        """
        # Check for encrypted token
        encrypted_var = os.getenv(f"{token_name}_ENCRYPTED")
        if encrypted_var:
            return self.decrypt_token(encrypted_var)
        
        # Check for AWS Secrets Manager
        aws_secret_name = os.getenv(f"{token_name}_SECRET_NAME")
        if aws_secret_name:
            return self._get_from_aws_secrets(aws_secret_name)
        
        # Fallback to plain env var (development only)
        plain_token = os.getenv(token_name)
        if plain_token:
            if os.getenv('NODE_ENV') == 'production':
                logger.warning(f"Plain text token in production: {token_name}")
            return plain_token
        
        return ""
    
    def _get_from_aws_secrets(self, secret_name: str) -> str:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            response = client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except ImportError:
            logger.warning("boto3 not installed, cannot use AWS Secrets Manager")
            return ""
        except ClientError as e:
            logger.error(f"Failed to retrieve secret from AWS: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret: {e}")
            return ""
    
    def mask_token(self, token: str, show_chars: int = 4) -> str:
        """Mask token for safe logging."""
        if not token or len(token) <= show_chars * 2:
            return "***"
        
        return f"{token[:show_chars]}...{token[-show_chars:]}"


# Global instance
security_manager = SecurityManager()


def get_secure_api_key(key_name: str = "OPENAI_API_KEY") -> str:
    """Get API key securely."""
    return security_manager.get_secure_token(key_name)


def get_secure_github_token() -> str:
    """Get GitHub token securely."""
    return security_manager.get_secure_token("GITHUB_TOKEN")
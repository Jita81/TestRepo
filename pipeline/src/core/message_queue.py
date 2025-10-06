"""
Message Queue Integration for Asynchronous Pipeline Processing.

This module provides RabbitMQ integration for decoupling pipeline stages
and enabling asynchronous, scalable processing.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional
from datetime import datetime

try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    pika = None

logger = logging.getLogger(__name__)


class MessageQueueConfig:
    """Configuration for RabbitMQ connection."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        heartbeat: int = 600,
        blocked_connection_timeout: int = 300
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat = heartbeat
        self.blocked_connection_timeout = blocked_connection_timeout


class MessageQueue:
    """
    RabbitMQ message queue implementation for pipeline stage communication.
    
    Provides:
    - Asynchronous message publishing
    - Message consumption with callbacks
    - Automatic reconnection
    - Dead letter queue handling
    - Message persistence
    """
    
    # Queue names
    TEXT_TO_VIDEO_QUEUE = "text_to_video"
    VIDEO_TO_3D_QUEUE = "video_to_3d"
    RESULT_QUEUE = "pipeline_results"
    ERROR_QUEUE = "pipeline_errors"
    
    def __init__(self, config: Optional[MessageQueueConfig] = None):
        """
        Initialize message queue.
        
        Args:
            config: RabbitMQ configuration
        """
        self.config = config or MessageQueueConfig()
        self.connection: Optional[Any] = None
        self.channel: Optional[Any] = None
        self._is_connected = False
        
        if not PIKA_AVAILABLE:
            logger.warning(
                "pika not available - message queue disabled. "
                "Install with: pip install pika"
            )
    
    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ.
        
        Returns:
            True if connected, False otherwise
        """
        if not PIKA_AVAILABLE:
            return False
        
        try:
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.virtual_host,
                credentials=credentials,
                heartbeat=self.config.heartbeat,
                blocked_connection_timeout=self.config.blocked_connection_timeout
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self._is_connected = True
            
            # Declare queues
            self._setup_queues()
            
            logger.info(
                f"Connected to RabbitMQ at {self.config.host}:{self.config.port}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._is_connected = False
            return False
    
    def _setup_queues(self):
        """Declare all required queues with proper configuration."""
        if not self.channel:
            return
        
        # Arguments for all queues
        queue_args = {
            'x-message-ttl': 3600000,  # 1 hour TTL
            'x-dead-letter-exchange': 'dlx',
            'x-dead-letter-routing-key': 'dead_letter'
        }
        
        # Declare dead letter exchange
        self.channel.exchange_declare(
            exchange='dlx',
            exchange_type='direct',
            durable=True
        )
        
        # Declare dead letter queue
        self.channel.queue_declare(
            queue='dead_letter_queue',
            durable=True
        )
        
        self.channel.queue_bind(
            exchange='dlx',
            queue='dead_letter_queue',
            routing_key='dead_letter'
        )
        
        # Declare pipeline queues
        for queue_name in [
            self.TEXT_TO_VIDEO_QUEUE,
            self.VIDEO_TO_3D_QUEUE,
            self.RESULT_QUEUE,
            self.ERROR_QUEUE
        ]:
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments=queue_args
            )
            logger.info(f"Declared queue: {queue_name}")
    
    def publish_message(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 0
    ) -> bool:
        """
        Publish a message to a queue.
        
        Args:
            queue_name: Target queue name
            message: Message payload (will be JSON-encoded)
            priority: Message priority (0-9)
        
        Returns:
            True if published successfully
        """
        if not self._is_connected or not self.channel:
            logger.warning("Not connected to RabbitMQ - message not sent")
            return False
        
        try:
            # Add metadata
            enriched_message = {
                **message,
                "_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "queue": queue_name,
                    "priority": priority
                }
            }
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(enriched_message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    priority=priority,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message to {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    def consume_messages(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], bool],
        auto_ack: bool = False
    ):
        """
        Consume messages from a queue.
        
        Args:
            queue_name: Queue to consume from
            callback: Function to process each message. Should return True on success.
            auto_ack: Whether to automatically acknowledge messages
        """
        if not self._is_connected or not self.channel:
            logger.error("Not connected to RabbitMQ")
            return
        
        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                logger.info(f"Received message from {queue_name}")
                
                # Process message
                success = callback(message)
                
                if success and not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                elif not success:
                    # Reject and requeue
                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=False  # Send to DLQ
                    )
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=on_message,
            auto_ack=auto_ack
        )
        
        logger.info(f"Started consuming from {queue_name}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
    
    def get_queue_size(self, queue_name: str) -> int:
        """
        Get the number of messages in a queue.
        
        Args:
            queue_name: Queue name
        
        Returns:
            Number of messages in queue
        """
        if not self._is_connected or not self.channel:
            return 0
        
        try:
            queue = self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                passive=True
            )
            return queue.method.message_count
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return 0
    
    def purge_queue(self, queue_name: str) -> bool:
        """
        Remove all messages from a queue.
        
        Args:
            queue_name: Queue name
        
        Returns:
            True if successful
        """
        if not self._is_connected or not self.channel:
            return False
        
        try:
            self.channel.queue_purge(queue=queue_name)
            logger.info(f"Purged queue: {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to purge queue: {e}")
            return False
    
    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        self._is_connected = False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncPipelineQueue:
    """
    Asynchronous wrapper for pipeline queue operations.
    
    Provides async/await interface for queue operations while
    maintaining compatibility with the existing pipeline.
    """
    
    def __init__(self, config: Optional[MessageQueueConfig] = None):
        self.queue = MessageQueue(config)
        self._executor = None
    
    async def connect(self) -> bool:
        """Asynchronously connect to RabbitMQ."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.queue.connect)
    
    async def publish_message(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 0
    ) -> bool:
        """Asynchronously publish a message."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.queue.publish_message,
            queue_name,
            message,
            priority
        )
    
    async def get_queue_size(self, queue_name: str) -> int:
        """Asynchronously get queue size."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.queue.get_queue_size,
            queue_name
        )
    
    async def close(self):
        """Asynchronously close connection."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.queue.close)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

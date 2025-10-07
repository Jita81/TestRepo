"""Queue client for inter-service communication."""

import json
import time
from typing import Callable, Optional
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from .logging_config import get_logger
from .exceptions import QueueError

logger = get_logger(__name__)


class QueueClient:
    """RabbitMQ client for pipeline message queue."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        retry_attempts: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize queue client.
        
        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: Authentication username
            password: Authentication password
            retry_attempts: Number of connection retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        
    def connect(self) -> None:
        """Establish connection to RabbitMQ with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                logger.info(
                    "connected_to_queue",
                    host=self.host,
                    port=self.port
                )
                return
                
            except AMQPConnectionError as e:
                logger.warning(
                    "queue_connection_failed",
                    attempt=attempt + 1,
                    max_attempts=self.retry_attempts,
                    error=str(e)
                )
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise QueueError(
                        f"Failed to connect to queue after {self.retry_attempts} attempts",
                        details={"host": self.host, "error": str(e)}
                    )
    
    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        Declare a queue.
        
        Args:
            queue_name: Name of the queue
            durable: Whether the queue should survive broker restart
        """
        if not self.channel:
            self.connect()
            
        try:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            logger.info("queue_declared", queue=queue_name, durable=durable)
        except AMQPChannelError as e:
            raise QueueError(
                f"Failed to declare queue: {queue_name}",
                details={"error": str(e)}
            )
    
    def publish(
        self,
        queue_name: str,
        message: dict,
        persistent: bool = True
    ) -> None:
        """
        Publish a message to a queue.
        
        Args:
            queue_name: Queue to publish to
            message: Message payload as dictionary
            persistent: Whether message should survive broker restart
        """
        if not self.channel:
            self.connect()
            
        try:
            properties = pika.BasicProperties(
                delivery_mode=2 if persistent else 1,
                content_type='application/json'
            )
            
            message_body = json.dumps(message)
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message_body,
                properties=properties
            )
            
            logger.info(
                "message_published",
                queue=queue_name,
                message_id=message.get('request_id')
            )
            
        except Exception as e:
            raise QueueError(
                f"Failed to publish message to queue: {queue_name}",
                details={"error": str(e)}
            )
    
    def consume(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ) -> None:
        """
        Start consuming messages from a queue.
        
        Args:
            queue_name: Queue to consume from
            callback: Function to call for each message
            auto_ack: Whether to auto-acknowledge messages
        """
        if not self.channel:
            self.connect()
            
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            logger.info("starting_consumer", queue=queue_name)
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("consumer_stopped", queue=queue_name)
            self.stop_consuming()
        except Exception as e:
            raise QueueError(
                f"Failed to consume from queue: {queue_name}",
                details={"error": str(e)}
            )
    
    def stop_consuming(self) -> None:
        """Stop consuming messages."""
        if self.channel:
            self.channel.stop_consuming()
    
    def acknowledge(self, delivery_tag: int) -> None:
        """
        Acknowledge a message.
        
        Args:
            delivery_tag: Delivery tag of the message
        """
        if self.channel:
            self.channel.basic_ack(delivery_tag=delivery_tag)
    
    def reject(self, delivery_tag: int, requeue: bool = True) -> None:
        """
        Reject a message.
        
        Args:
            delivery_tag: Delivery tag of the message
            requeue: Whether to requeue the message
        """
        if self.channel:
            self.channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)
    
    def close(self) -> None:
        """Close the connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("queue_connection_closed")
        except Exception as e:
            logger.error("error_closing_connection", error=str(e))
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
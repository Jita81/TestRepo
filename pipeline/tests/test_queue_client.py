"""Tests for queue client."""

import pytest
from unittest.mock import MagicMock, patch
import pika
from common.queue_client import QueueClient
from common.exceptions import QueueError


class TestQueueClientInit:
    """Tests for QueueClient initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        client = QueueClient()
        assert client.host == "localhost"
        assert client.port == 5672
        assert client.username == "guest"
        assert client.password == "guest"
        assert client.retry_attempts == 3
        assert client.retry_delay == 5
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        client = QueueClient(
            host="custom-host",
            port=5673,
            username="admin",
            password="secret",
            retry_attempts=5,
            retry_delay=10
        )
        assert client.host == "custom-host"
        assert client.port == 5673
        assert client.username == "admin"
        assert client.password == "secret"
        assert client.retry_attempts == 5
        assert client.retry_delay == 10


class TestQueueClientConnection:
    """Tests for queue client connection."""
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_successful_connection(self, mock_connection):
        """Test successful connection to RabbitMQ."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn
        
        client = QueueClient()
        client.connect()
        
        assert client.connection is not None
        assert client.channel is not None
        mock_connection.assert_called_once()
    
    @patch('common.queue_client.pika.BlockingConnection')
    @patch('common.queue_client.time.sleep')
    def test_connection_retry(self, mock_sleep, mock_connection):
        """Test connection retry mechanism."""
        # Fail twice, succeed on third attempt
        mock_connection.side_effect = [
            pika.exceptions.AMQPConnectionError("Connection failed"),
            pika.exceptions.AMQPConnectionError("Connection failed"),
            MagicMock()
        ]
        
        client = QueueClient(retry_attempts=3, retry_delay=1)
        client.connect()
        
        # Should have tried 3 times
        assert mock_connection.call_count == 3
        # Should have slept twice (between retries)
        assert mock_sleep.call_count == 2
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_connection_failure_after_retries(self, mock_connection):
        """Test that QueueError is raised after all retries fail."""
        mock_connection.side_effect = pika.exceptions.AMQPConnectionError("Failed")
        
        client = QueueClient(retry_attempts=2)
        
        with pytest.raises(QueueError) as exc_info:
            client.connect()
        
        assert "Failed to connect" in str(exc_info.value)


class TestQueueClientOperations:
    """Tests for queue client operations."""
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_declare_queue(self, mock_connection):
        """Test queue declaration."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn
        
        client = QueueClient()
        client.connect()
        client.declare_queue("test_queue")
        
        mock_channel.queue_declare.assert_called_once_with(
            queue="test_queue",
            durable=True
        )
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_publish_message(self, mock_connection):
        """Test message publishing."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn
        
        client = QueueClient()
        client.connect()
        
        message = {"request_id": "req_123", "data": "test"}
        client.publish("test_queue", message)
        
        mock_channel.basic_publish.assert_called_once()
        args = mock_channel.basic_publish.call_args
        assert args[1]["routing_key"] == "test_queue"
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_acknowledge_message(self, mock_connection):
        """Test message acknowledgment."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn
        
        client = QueueClient()
        client.connect()
        client.acknowledge(delivery_tag=1)
        
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_reject_message(self, mock_connection):
        """Test message rejection."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection.return_value = mock_conn
        
        client = QueueClient()
        client.connect()
        client.reject(delivery_tag=1, requeue=True)
        
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag=1,
            requeue=True
        )


class TestQueueClientContextManager:
    """Tests for context manager usage."""
    
    @patch('common.queue_client.pika.BlockingConnection')
    def test_context_manager(self, mock_connection):
        """Test using queue client as context manager."""
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_conn.is_closed = False
        mock_connection.return_value = mock_conn
        
        with QueueClient() as client:
            assert client.connection is not None
        
        # Connection should be closed after exiting context
        mock_conn.close.assert_called_once()
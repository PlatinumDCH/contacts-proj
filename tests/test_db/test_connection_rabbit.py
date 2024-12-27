import pytest
from unittest.mock import patch, AsyncMock
from aio_pika import exceptions

from app.db.get_rab_con import RaabbitMQConnectionManager

@pytest.fixture
def rabbitmq_connection_params():
    """Фикстура для предоставления параметров подключения к RabbitMQ."""
    url = "amqp://guest:guest@localhost:5672/"
    retries = 2
    delay = 0.1
    return url, retries, delay

@pytest.fixture
def mock_rabbitmq_connection():
    """Фикстура для подмены connect_robust на мок-объект."""
    mock_connection = AsyncMock()
    with patch('app.db.get_rab_con.connect_robust', return_value=mock_connection) as mock_connect:
        yield mock_connection, mock_connect



class TestRabbitMQConnectionManager:

    @pytest.mark.asyncio
    async def test_connect(self, rabbitmq_connection_params, mock_rabbitmq_connection):
        """Test successful connection."""
        url, retries, delay = rabbitmq_connection_params
        mock_connection, mock_connect = mock_rabbitmq_connection

        manager = RaabbitMQConnectionManager(url, retries, delay)
        connection = await manager.connect()

        mock_connect.assert_called_once_with(url)
        assert connection == mock_connection

    @pytest.mark.asyncio
    async def test_connect_failure(self, rabbitmq_connection_params):
        """Test failed connection to RabbitMQ."""
        url, retries, delay = rabbitmq_connection_params

        with patch('app.db.get_rab_con.connect_robust', side_effect=exceptions.AMQPConnectionError("Connection error")):
            manager = RaabbitMQConnectionManager(url, retries, delay)
            with pytest.raises(RuntimeError) as exc_info:
                await manager.connect()

            assert str(exc_info.value) == 'Could not connect to RabbitMQ'

  
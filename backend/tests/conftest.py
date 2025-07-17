import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import boto3
from moto import mock_dynamodb

from app.main import app
from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user."""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "role": "admin"
    }


@pytest.fixture
def auth_headers(mock_auth_user):
    """Authentication headers for API requests."""
    with patch('app.utils.auth.get_current_user', return_value=mock_auth_user):
        yield {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB for testing."""
    with mock_dynamodb():
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create test tables
        create_projects_table(dynamodb)
        create_agents_table(dynamodb)
        create_messages_table(dynamodb)
        create_tasks_table(dynamodb)
        create_channels_table(dynamodb)
        create_artifacts_table(dynamodb)
        create_ws_connections_table(dynamodb)
        
        yield dynamodb


def create_projects_table(dynamodb):
    """Create projects table for testing."""
    table = dynamodb.create_table(
        TableName=settings.projects_table,
        KeySchema=[
            {'AttributeName': 'project_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'project_id', 'AttributeType': 'S'},
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'created_at', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'user-projects-index',
                'KeySchema': [
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'IndexName': 'status-index',
                'KeySchema': [
                    {'AttributeName': 'status', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_agents_table(dynamodb):
    """Create agents table for testing."""
    table = dynamodb.create_table(
        TableName=settings.agents_table,
        KeySchema=[
            {'AttributeName': 'agent_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'agent_id', 'AttributeType': 'S'},
            {'AttributeName': 'project_id', 'AttributeType': 'S'},
            {'AttributeName': 'agent_type', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'project-agents-index',
                'KeySchema': [
                    {'AttributeName': 'project_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'agent_type', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_messages_table(dynamodb):
    """Create messages table for testing."""
    table = dynamodb.create_table(
        TableName=settings.messages_table,
        KeySchema=[
            {'AttributeName': 'channel_id', 'KeyType': 'HASH'},
            {'AttributeName': 'message_id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'channel_id', 'AttributeType': 'S'},
            {'AttributeName': 'message_id', 'AttributeType': 'S'},
            {'AttributeName': 'sender_id', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'sender-messages-index',
                'KeySchema': [
                    {'AttributeName': 'sender_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_tasks_table(dynamodb):
    """Create tasks table for testing."""
    table = dynamodb.create_table(
        TableName=settings.tasks_table,
        KeySchema=[
            {'AttributeName': 'task_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'task_id', 'AttributeType': 'S'},
            {'AttributeName': 'project_id', 'AttributeType': 'S'},
            {'AttributeName': 'created_at', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'project-tasks-index',
                'KeySchema': [
                    {'AttributeName': 'project_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_channels_table(dynamodb):
    """Create channels table for testing."""
    table = dynamodb.create_table(
        TableName=settings.channels_table,
        KeySchema=[
            {'AttributeName': 'channel_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'channel_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_artifacts_table(dynamodb):
    """Create artifacts table for testing."""
    table = dynamodb.create_table(
        TableName=settings.artifacts_table,
        KeySchema=[
            {'AttributeName': 'artifact_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'artifact_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


def create_ws_connections_table(dynamodb):
    """Create WebSocket connections table for testing."""
    table = dynamodb.create_table(
        TableName=settings.ws_connections_table,
        KeySchema=[
            {'AttributeName': 'connection_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'connection_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    return table


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "project_type": "web_application",
        "complexity": "medium",
        "requirements": [
            {
                "id": "req_001",
                "title": "User Registration",
                "description": "Users should be able to register",
                "priority": "high",
                "category": "functional"
            }
        ],
        "metadata": {
            "tags": ["test", "demo"],
            "tech_stack": ["React", "FastAPI", "DynamoDB"],
            "target_audience": "Developers",
            "business_goals": ["Improve efficiency"]
        }
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Agent",
        "agent_type": "pm",
        "project_id": "test_project_123",
        "description": "A test agent for unit testing"
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "channel_id": "test_channel_123",
        "content": "Hello, this is a test message",
        "message_type": "text"
    }
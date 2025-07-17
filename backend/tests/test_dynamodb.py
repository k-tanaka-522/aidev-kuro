import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from botocore.exceptions import ClientError

from app.services.dynamodb import DynamoDBService


class TestDynamoDBService:
    """Test suite for DynamoDB service."""

    @pytest.fixture
    def db_service(self):
        """Create DynamoDB service instance."""
        return DynamoDBService()

    def test_serialize_item(self, db_service):
        """Test item serialization for DynamoDB."""
        test_item = {
            "string_field": "test_value",
            "datetime_field": datetime(2024, 1, 1, 12, 0, 0),
            "dict_field": {"key": "value"},
            "list_field": ["item1", "item2"],
            "number_field": 42
        }
        
        serialized = db_service._serialize_item(test_item)
        
        assert serialized["string_field"] == "test_value"
        assert serialized["datetime_field"] == "2024-01-01T12:00:00"
        assert '"key": "value"' in serialized["dict_field"]
        assert '"item1", "item2"' in serialized["list_field"]
        assert serialized["number_field"] == 42

    def test_deserialize_item(self, db_service):
        """Test item deserialization from DynamoDB."""
        test_item = {
            "string_field": "test_value",
            "created_at": "2024-01-01T12:00:00",
            "requirements": '["req1", "req2"]',
            "metadata": '{"key": "value"}',
            "number_field": 42
        }
        
        deserialized = db_service._deserialize_item(test_item)
        
        assert deserialized["string_field"] == "test_value"
        assert isinstance(deserialized["created_at"], datetime)
        assert deserialized["requirements"] == ["req1", "req2"]
        assert deserialized["metadata"] == {"key": "value"}
        assert deserialized["number_field"] == 42

    @pytest.mark.asyncio
    async def test_create_project_success(self, db_service):
        """Test successful project creation."""
        project_data = {
            "name": "Test Project",
            "description": "Test description",
            "user_id": "test_user_123"
        }
        
        with patch.object(db_service.projects_table, 'put_item') as mock_put:
            mock_put.return_value = {}
            
            result = await db_service.create_project(project_data)
            
            assert result["name"] == "Test Project"
            assert "project_id" in result
            assert "created_at" in result
            assert "updated_at" in result
            mock_put.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_duplicate_id(self, db_service):
        """Test project creation with duplicate ID."""
        project_data = {
            "project_id": "existing_project",
            "name": "Test Project",
            "user_id": "test_user_123"
        }
        
        with patch.object(db_service.projects_table, 'put_item') as mock_put:
            mock_put.side_effect = ClientError(
                error_response={'Error': {'Code': 'ConditionalCheckFailedException'}},
                operation_name='PutItem'
            )
            
            with pytest.raises(ValueError, match="Project with this ID already exists"):
                await db_service.create_project(project_data)

    @pytest.mark.asyncio
    async def test_get_project_success(self, db_service):
        """Test successful project retrieval."""
        project_id = "test_project_123"
        
        mock_item = {
            "project_id": project_id,
            "name": "Test Project",
            "created_at": "2024-01-01T12:00:00",
            "requirements": '[]',
            "metadata": '{}'
        }
        
        with patch.object(db_service.projects_table, 'get_item') as mock_get:
            mock_get.return_value = {"Item": mock_item}
            
            result = await db_service.get_project(project_id)
            
            assert result["project_id"] == project_id
            assert result["name"] == "Test Project"
            assert isinstance(result["created_at"], datetime)
            mock_get.assert_called_once_with(Key={'project_id': project_id})

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, db_service):
        """Test project retrieval when project doesn't exist."""
        project_id = "nonexistent_project"
        
        with patch.object(db_service.projects_table, 'get_item') as mock_get:
            mock_get.return_value = {}  # No Item key
            
            result = await db_service.get_project(project_id)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_update_project_success(self, db_service):
        """Test successful project update."""
        project_id = "test_project_123"
        update_data = {
            "name": "Updated Project",
            "description": "Updated description"
        }
        
        mock_updated_item = {
            "project_id": project_id,
            "name": "Updated Project",
            "description": "Updated description",
            "updated_at": "2024-01-01T12:00:00"
        }
        
        with patch.object(db_service.projects_table, 'update_item') as mock_update:
            mock_update.return_value = {"Attributes": mock_updated_item}
            
            result = await db_service.update_project(project_id, update_data)
            
            assert result["name"] == "Updated Project"
            assert result["description"] == "Updated description"
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_project_success(self, db_service):
        """Test successful project deletion."""
        project_id = "test_project_123"
        
        with patch.object(db_service.projects_table, 'delete_item') as mock_delete:
            mock_delete.return_value = {}
            
            result = await db_service.delete_project(project_id)
            
            assert result is True
            mock_delete.assert_called_once_with(
                Key={'project_id': project_id},
                ConditionExpression=mock_delete.call_args[1]['ConditionExpression']
            )

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, db_service):
        """Test project deletion when project doesn't exist."""
        project_id = "nonexistent_project"
        
        with patch.object(db_service.projects_table, 'delete_item') as mock_delete:
            mock_delete.side_effect = ClientError(
                error_response={'Error': {'Code': 'ConditionalCheckFailedException'}},
                operation_name='DeleteItem'
            )
            
            result = await db_service.delete_project(project_id)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_list_projects_by_user(self, db_service):
        """Test listing projects by user ID."""
        user_id = "test_user_123"
        
        mock_items = [
            {
                "project_id": "proj_001",
                "user_id": user_id,
                "name": "Project 1",
                "created_at": "2024-01-01T12:00:00"
            },
            {
                "project_id": "proj_002", 
                "user_id": user_id,
                "name": "Project 2",
                "created_at": "2024-01-02T12:00:00"
            }
        ]
        
        with patch.object(db_service.projects_table, 'query') as mock_query:
            mock_query.return_value = {
                "Items": mock_items,
                "Count": 2
            }
            
            result = await db_service.list_projects(user_id=user_id)
            
            assert len(result["items"]) == 2
            assert result["count"] == 2
            assert result["items"][0]["name"] == "Project 1"
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_projects_with_status_filter(self, db_service):
        """Test listing projects with status filter."""
        user_id = "test_user_123"
        status = "active"
        
        with patch.object(db_service.projects_table, 'query') as mock_query:
            mock_query.return_value = {
                "Items": [],
                "Count": 0
            }
            
            await db_service.list_projects(user_id=user_id, status=status)
            
            # Verify that FilterExpression was used
            call_args = mock_query.call_args[1]
            assert 'FilterExpression' in call_args

    @pytest.mark.asyncio
    async def test_get_project_stats(self, db_service):
        """Test getting project statistics."""
        user_id = "test_user_123"
        
        mock_projects = [
            {
                "status": "active",
                "total_tasks": 10,
                "completed_tasks": 5
            },
            {
                "status": "completed",
                "total_tasks": 8,
                "completed_tasks": 8
            },
            {
                "status": "draft",
                "total_tasks": 0,
                "completed_tasks": 0
            }
        ]
        
        with patch.object(db_service.projects_table, 'query') as mock_query:
            mock_query.return_value = {"Items": mock_projects}
            
            result = await db_service.get_project_stats(user_id=user_id)
            
            assert result["total_projects"] == 3
            assert result["active_projects"] == 1
            assert result["completed_projects"] == 1
            assert result["draft_projects"] == 1
            assert result["total_tasks"] == 18
            assert result["completed_tasks"] == 13
            assert result["average_completion_rate"] == (13/18) * 100

    @pytest.mark.asyncio
    async def test_health_check_success(self, db_service):
        """Test successful health check."""
        with patch.object(db_service.projects_table, 'table_status', 'ACTIVE'):
            result = await db_service.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_service):
        """Test health check failure."""
        with patch.object(db_service.projects_table, 'table_status', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                await db_service.health_check()
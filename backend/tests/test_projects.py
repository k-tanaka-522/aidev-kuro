import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.models.project import ProjectStatus


class TestProjectsAPI:
    """Test suite for Projects API endpoints."""

    def test_create_project_success(self, client, auth_headers, sample_project_data):
        """Test successful project creation."""
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.create_project') as mock_create:
            
            # Mock authentication
            mock_auth.return_value = {
                "user_id": "test_user_123",
                "email": "test@example.com",
                "name": "Test User",
                "role": "admin"
            }
            
            # Mock DynamoDB response
            mock_project = {
                **sample_project_data,
                "project_id": "proj_123456789abc",
                "user_id": "test_user_123",
                "status": "draft",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "progress_percentage": 0.0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "assigned_agents": [],
                "active_agents": [],
                "team_members": [],
                "channels": [],
                "settings": {}
            }
            mock_create.return_value = mock_project
            
            response = client.post(
                "/api/v1/projects/",
                json=sample_project_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == sample_project_data["name"]
            assert data["project_id"] == "proj_123456789abc"
            assert data["user_id"] == "test_user_123"
            assert data["status"] == "draft"

    def test_create_project_validation_error(self, client, auth_headers):
        """Test project creation with validation errors."""
        with patch('app.utils.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            # Invalid data - missing required fields
            invalid_data = {
                "description": "Missing name field"
            }
            
            response = client.post(
                "/api/v1/projects/",
                json=invalid_data,
                headers=auth_headers
            )
            
            assert response.status_code == 422

    def test_get_project_success(self, client, auth_headers):
        """Test successful project retrieval."""
        project_id = "proj_123456789abc"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            mock_project = {
                "project_id": project_id,
                "name": "Test Project",
                "description": "Test description",
                "user_id": "test_user_123",
                "status": "active",
                "project_type": "web_application",
                "complexity": "medium",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "progress_percentage": 25.0,
                "requirements": [],
                "metadata": {},
                "total_tasks": 4,
                "completed_tasks": 1,
                "assigned_agents": [],
                "active_agents": [],
                "team_members": [],
                "channels": [],
                "settings": {}
            }
            mock_get.return_value = mock_project
            
            response = client.get(
                f"/api/v1/projects/{project_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["project_id"] == project_id
            assert data["name"] == "Test Project"

    def test_get_project_not_found(self, client, auth_headers):
        """Test project retrieval when project doesn't exist."""
        project_id = "nonexistent_project"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            mock_get.return_value = None
            
            response = client.get(
                f"/api/v1/projects/{project_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 404

    def test_get_project_access_denied(self, client, auth_headers):
        """Test project retrieval with insufficient permissions."""
        project_id = "proj_123456789abc"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get:
            
            mock_auth.return_value = {"user_id": "other_user_456"}
            
            mock_project = {
                "project_id": project_id,
                "user_id": "test_user_123",  # Different user
                "team_members": [],  # Not in team
                "name": "Test Project"
            }
            mock_get.return_value = mock_project
            
            response = client.get(
                f"/api/v1/projects/{project_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 403

    def test_update_project_success(self, client, auth_headers):
        """Test successful project update."""
        project_id = "proj_123456789abc"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get, \
             patch('app.services.dynamodb.DynamoDBService.update_project') as mock_update:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            # Existing project
            mock_get.return_value = {
                "project_id": project_id,
                "user_id": "test_user_123",
                "name": "Old Name"
            }
            
            # Updated project
            updated_project = {
                "project_id": project_id,
                "user_id": "test_user_123",
                "name": "Updated Name",
                "description": "Updated description",
                "status": "active"
            }
            mock_update.return_value = updated_project
            
            update_data = {
                "name": "Updated Name",
                "description": "Updated description"
            }
            
            response = client.put(
                f"/api/v1/projects/{project_id}",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"

    def test_delete_project_success(self, client, auth_headers):
        """Test successful project deletion."""
        project_id = "proj_123456789abc"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get, \
             patch('app.services.dynamodb.DynamoDBService.delete_project') as mock_delete:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            mock_get.return_value = {
                "project_id": project_id,
                "user_id": "test_user_123"
            }
            mock_delete.return_value = True
            
            response = client.delete(
                f"/api/v1/projects/{project_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 204

    def test_list_projects_success(self, client, auth_headers):
        """Test successful project listing."""
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.list_projects') as mock_list:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            mock_projects = [
                {
                    "project_id": "proj_001",
                    "name": "Project 1",
                    "status": "active",
                    "user_id": "test_user_123",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "progress_percentage": 50.0,
                    "requirements": [],
                    "metadata": {},
                    "project_type": "web_application",
                    "complexity": "medium",
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "assigned_agents": [],
                    "active_agents": [],
                    "team_members": [],
                    "channels": [],
                    "settings": {}
                },
                {
                    "project_id": "proj_002",
                    "name": "Project 2",
                    "status": "draft",
                    "user_id": "test_user_123",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "progress_percentage": 0.0,
                    "requirements": [],
                    "metadata": {},
                    "project_type": "mobile_app",
                    "complexity": "high",
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "assigned_agents": [],
                    "active_agents": [],
                    "team_members": [],
                    "channels": [],
                    "settings": {}
                }
            ]
            
            mock_list.return_value = {
                "items": mock_projects,
                "count": 2,
                "last_evaluated_key": None
            }
            
            response = client.get(
                "/api/v1/projects/",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["projects"]) == 2
            assert data["total"] == 2
            assert data["page"] == 1
            assert data["has_next"] == False

    def test_start_project_success(self, client, auth_headers):
        """Test successful project start."""
        project_id = "proj_123456789abc"
        
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get, \
             patch('app.services.dynamodb.DynamoDBService.update_project') as mock_update:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            mock_get.return_value = {
                "project_id": project_id,
                "user_id": "test_user_123",
                "status": "draft"
            }
            
            started_project = {
                "project_id": project_id,
                "user_id": "test_user_123",
                "status": "active",
                "started_at": datetime.utcnow()
            }
            mock_update.return_value = started_project
            
            response = client.post(
                f"/api/v1/projects/{project_id}/start",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "active"

    def test_get_project_stats_success(self, client, auth_headers):
        """Test successful project statistics retrieval."""
        with patch('app.utils.auth.get_current_user') as mock_auth, \
             patch('app.services.dynamodb.DynamoDBService.get_project_stats') as mock_stats:
            
            mock_auth.return_value = {"user_id": "test_user_123"}
            
            mock_stats_data = {
                "total_projects": 5,
                "active_projects": 2,
                "completed_projects": 2,
                "draft_projects": 1,
                "total_tasks": 20,
                "completed_tasks": 15,
                "average_completion_rate": 75.0
            }
            mock_stats.return_value = mock_stats_data
            
            response = client.get(
                "/api/v1/projects/stats/summary",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_projects"] == 5
            assert data["active_projects"] == 2
            assert data["average_completion_rate"] == 75.0

    def test_unauthorized_access(self, client):
        """Test unauthorized access to projects API."""
        response = client.get("/api/v1/projects/")
        assert response.status_code == 403  # No authorization header
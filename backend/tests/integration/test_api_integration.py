import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


class TestAPIIntegration:
    """Integration tests for the complete API."""

    @pytest.fixture
    def integration_client(self):
        """Create test client for integration tests."""
        return TestClient(app)

    def test_complete_project_workflow(self, integration_client):
        """Test complete project workflow from creation to completion."""
        
        # Mock authentication for all requests
        mock_user = {
            "user_id": "integration_test_user",
            "email": "integration@example.com", 
            "name": "Integration Test User",
            "role": "admin"
        }
        
        with patch('app.utils.auth.get_current_user', return_value=mock_user), \
             patch('app.services.dynamodb.DynamoDBService.create_project') as mock_create, \
             patch('app.services.dynamodb.DynamoDBService.get_project') as mock_get, \
             patch('app.services.dynamodb.DynamoDBService.update_project') as mock_update, \
             patch('app.services.dynamodb.DynamoDBService.list_projects') as mock_list:
            
            project_data = {
                "name": "Integration Test Project",
                "description": "A project for integration testing",
                "project_type": "web_application",
                "complexity": "medium"
            }
            
            # Step 1: Create project
            created_project = {
                **project_data,
                "project_id": "proj_integration_123",
                "user_id": mock_user["user_id"],
                "status": "draft",
                "progress_percentage": 0.0,
                "requirements": [],
                "metadata": {},
                "total_tasks": 0,
                "completed_tasks": 0,
                "assigned_agents": [],
                "active_agents": [],
                "team_members": [],
                "channels": [],
                "settings": {}
            }
            mock_create.return_value = created_project
            
            response = integration_client.post(
                "/api/v1/projects/",
                json=project_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 201
            project = response.json()
            project_id = project["project_id"]
            
            # Step 2: Get project details
            mock_get.return_value = created_project
            
            response = integration_client.get(
                f"/api/v1/projects/{project_id}",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            project_details = response.json()
            assert project_details["name"] == project_data["name"]
            
            # Step 3: Start project
            started_project = {
                **created_project,
                "status": "active"
            }
            mock_get.return_value = created_project
            mock_update.return_value = started_project
            
            response = integration_client.post(
                f"/api/v1/projects/{project_id}/start",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "active"
            
            # Step 4: Update project progress
            updated_project = {
                **started_project,
                "progress_percentage": 50.0,
                "completed_tasks": 2,
                "total_tasks": 4
            }
            mock_get.return_value = started_project
            mock_update.return_value = updated_project
            
            response = integration_client.put(
                f"/api/v1/projects/{project_id}",
                json={"progress_percentage": 50.0},
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            assert response.json()["progress_percentage"] == 50.0
            
            # Step 5: Complete project
            completed_project = {
                **updated_project,
                "status": "completed",
                "progress_percentage": 100.0
            }
            mock_get.return_value = updated_project
            mock_update.return_value = completed_project
            
            response = integration_client.post(
                f"/api/v1/projects/{project_id}/complete",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "completed"
            
            # Step 6: List projects
            mock_list.return_value = {
                "items": [completed_project],
                "count": 1,
                "last_evaluated_key": None
            }
            
            response = integration_client.get(
                "/api/v1/projects/",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            projects_list = response.json()
            assert len(projects_list["projects"]) == 1
            assert projects_list["projects"][0]["status"] == "completed"

    def test_agents_and_messages_integration(self, integration_client):
        """Test agents and messages integration."""
        
        mock_user = {
            "user_id": "integration_test_user",
            "email": "integration@example.com",
            "name": "Integration Test User",
            "role": "admin"
        }
        
        with patch('app.utils.auth.get_current_user', return_value=mock_user):
            
            # Step 1: List available agents
            response = integration_client.get(
                "/api/v1/agents/",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            agents = response.json()
            assert len(agents) >= 3  # PM, Architect, Security
            
            # Step 2: Get channels
            response = integration_client.get(
                "/api/v1/messages/channels",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            channels = response.json()
            assert len(channels) >= 1
            
            # Step 3: Send message to channel
            if channels:
                channel_id = channels[0]["channel_id"]
                
                message_data = {
                    "channel_id": channel_id,
                    "content": "Hello from integration test",
                    "message_type": "text"
                }
                
                response = integration_client.post(
                    "/api/v1/messages/",
                    json=message_data,
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 200
                message = response.json()
                assert message["content"] == "Hello from integration test"
                
                # Step 4: Get messages from channel
                response = integration_client.get(
                    f"/api/v1/messages/{channel_id}",
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 200
                messages = response.json()
                assert len(messages) >= 1

    def test_artifacts_integration(self, integration_client):
        """Test artifacts management integration."""
        
        mock_user = {
            "user_id": "integration_test_user",
            "email": "integration@example.com",
            "name": "Integration Test User",
            "role": "admin"
        }
        
        with patch('app.utils.auth.get_current_user', return_value=mock_user):
            
            # Step 1: List artifacts
            response = integration_client.get(
                "/api/v1/artifacts/",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            artifacts = response.json()
            assert isinstance(artifacts, list)
            
            # Step 2: Create artifact
            artifact_data = {
                "name": "Integration Test Artifact",
                "artifact_type": "document",
                "project_id": "proj_integration_123",
                "description": "Test artifact for integration testing"
            }
            
            response = integration_client.post(
                "/api/v1/artifacts/",
                json=artifact_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            artifact = response.json()
            artifact_id = artifact["artifact_id"]
            
            # Step 3: Get artifact details
            response = integration_client.get(
                f"/api/v1/artifacts/{artifact_id}",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            artifact_details = response.json()
            assert artifact_details["name"] == artifact_data["name"]

    def test_error_handling_integration(self, integration_client):
        """Test error handling across different endpoints."""
        
        # Test 401 Unauthorized
        response = integration_client.get("/api/v1/projects/")
        assert response.status_code == 403  # No auth header
        
        # Test 404 Not Found with auth
        mock_user = {"user_id": "test_user"}
        
        with patch('app.utils.auth.get_current_user', return_value=mock_user), \
             patch('app.services.dynamodb.DynamoDBService.get_project', return_value=None):
            
            response = integration_client.get(
                "/api/v1/projects/nonexistent",
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 404
            
        # Test 422 Validation Error
        with patch('app.utils.auth.get_current_user', return_value=mock_user):
            
            invalid_data = {"invalid_field": "value"}
            
            response = integration_client.post(
                "/api/v1/projects/",
                json=invalid_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 422

    def test_health_endpoints_integration(self, integration_client):
        """Test health and status endpoints."""
        
        # Test root endpoint
        response = integration_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
        # Test health endpoint
        with patch('app.services.dynamodb.DynamoDBService.health_check', return_value=True):
            response = integration_client.get("/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
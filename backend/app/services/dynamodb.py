import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime
import uuid
import json

from app.config import settings


logger = structlog.get_logger()


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        # Table references
        self.projects_table = self.dynamodb.Table(settings.projects_table)
        self.agents_table = self.dynamodb.Table(settings.agents_table)
        self.messages_table = self.dynamodb.Table(settings.messages_table)
        self.tasks_table = self.dynamodb.Table(settings.tasks_table)
        self.channels_table = self.dynamodb.Table(settings.channels_table)
        self.artifacts_table = self.dynamodb.Table(settings.artifacts_table)
        self.ws_connections_table = self.dynamodb.Table(settings.ws_connections_table)

    async def health_check(self) -> bool:
        """Check if DynamoDB is accessible"""
        try:
            self.projects_table.table_status
            return True
        except Exception as e:
            logger.error("DynamoDB health check failed", error=str(e))
            raise

    def _serialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize item for DynamoDB storage"""
        serialized = {}
        for key, value in item.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                serialized[key] = json.dumps(value, default=str)
            else:
                serialized[key] = value
        return serialized

    def _deserialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize item from DynamoDB"""
        if not item:
            return item
            
        deserialized = {}
        for key, value in item.items():
            if isinstance(value, str) and key in ['created_at', 'updated_at', 'started_at', 'completed_at', 'deadline']:
                try:
                    deserialized[key] = datetime.fromisoformat(value)
                except ValueError:
                    deserialized[key] = value
            elif isinstance(value, str) and key in ['requirements', 'metadata', 'settings', 'assigned_agents', 'team_members', 'channels']:
                try:
                    deserialized[key] = json.loads(value)
                except json.JSONDecodeError:
                    deserialized[key] = value
            else:
                deserialized[key] = value
        return deserialized

    # Project operations
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        try:
            # Generate project ID if not provided
            if 'project_id' not in project_data:
                project_data['project_id'] = f"proj_{uuid.uuid4().hex[:12]}"
            
            # Set timestamps
            now = datetime.utcnow()
            project_data['created_at'] = now
            project_data['updated_at'] = now
            
            # Serialize for storage
            serialized_data = self._serialize_item(project_data)
            
            # Store in DynamoDB
            response = self.projects_table.put_item(
                Item=serialized_data,
                ConditionExpression='attribute_not_exists(project_id)'
            )
            
            logger.info("Project created", project_id=project_data['project_id'])
            return self._deserialize_item(serialized_data)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Project with this ID already exists")
            logger.error("Failed to create project", error=str(e))
            raise

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            response = self.projects_table.get_item(
                Key={'project_id': project_id}
            )
            
            if 'Item' not in response:
                return None
                
            return self._deserialize_item(response['Item'])
            
        except ClientError as e:
            logger.error("Failed to get project", project_id=project_id, error=str(e))
            raise

    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update project"""
        try:
            # Set update timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Build update expression
            update_expression = "SET "
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in update_data.items():
                safe_key = f"#attr_{key}"
                value_key = f":val_{key}"
                
                update_expression += f"{safe_key} = {value_key}, "
                expression_attribute_names[safe_key] = key
                
                if isinstance(value, datetime):
                    expression_attribute_values[value_key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    expression_attribute_values[value_key] = json.dumps(value, default=str)
                else:
                    expression_attribute_values[value_key] = value
            
            # Remove trailing comma and space
            update_expression = update_expression.rstrip(", ")
            
            response = self.projects_table.update_item(
                Key={'project_id': project_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            logger.info("Project updated", project_id=project_id)
            return self._deserialize_item(response['Attributes'])
            
        except ClientError as e:
            logger.error("Failed to update project", project_id=project_id, error=str(e))
            raise

    async def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        try:
            self.projects_table.delete_item(
                Key={'project_id': project_id},
                ConditionExpression='attribute_exists(project_id)'
            )
            
            logger.info("Project deleted", project_id=project_id)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            logger.error("Failed to delete project", project_id=project_id, error=str(e))
            raise

    async def list_projects(
        self, 
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        last_evaluated_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List projects with optional filtering"""
        try:
            query_kwargs = {
                'Limit': limit,
                'ScanIndexForward': False  # Sort by created_at descending
            }
            
            if last_evaluated_key:
                query_kwargs['ExclusiveStartKey'] = last_evaluated_key
            
            if user_id:
                # Query by user_id using GSI
                query_kwargs['IndexName'] = 'user-projects-index'
                query_kwargs['KeyConditionExpression'] = Key('user_id').eq(user_id)
                
                if status:
                    query_kwargs['FilterExpression'] = Attr('status').eq(status)
                
                response = self.projects_table.query(**query_kwargs)
            else:
                # Scan all projects
                if status:
                    query_kwargs['FilterExpression'] = Attr('status').eq(status)
                
                response = self.projects_table.scan(**query_kwargs)
            
            items = [self._deserialize_item(item) for item in response.get('Items', [])]
            
            return {
                'items': items,
                'last_evaluated_key': response.get('LastEvaluatedKey'),
                'count': response.get('Count', 0)
            }
            
        except ClientError as e:
            logger.error("Failed to list projects", error=str(e))
            raise

    async def get_project_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get project statistics"""
        try:
            query_kwargs = {}
            
            if user_id:
                query_kwargs['IndexName'] = 'user-projects-index'
                query_kwargs['KeyConditionExpression'] = Key('user_id').eq(user_id)
                response = self.projects_table.query(**query_kwargs)
            else:
                response = self.projects_table.scan(**query_kwargs)
            
            projects = [self._deserialize_item(item) for item in response.get('Items', [])]
            
            stats = {
                'total_projects': len(projects),
                'active_projects': len([p for p in projects if p.get('status') == 'active']),
                'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
                'draft_projects': len([p for p in projects if p.get('status') == 'draft']),
                'total_tasks': sum(p.get('total_tasks', 0) for p in projects),
                'completed_tasks': sum(p.get('completed_tasks', 0) for p in projects),
            }
            
            # Calculate average completion rate
            if stats['total_tasks'] > 0:
                stats['average_completion_rate'] = (stats['completed_tasks'] / stats['total_tasks']) * 100
            else:
                stats['average_completion_rate'] = 0.0
            
            return stats
            
        except ClientError as e:
            logger.error("Failed to get project stats", error=str(e))
            raise
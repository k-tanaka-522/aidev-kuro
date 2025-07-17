from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from typing import Optional, List
import structlog

from app.models.project import (
    Project, CreateProjectRequest, UpdateProjectRequest, 
    ProjectListResponse, ProjectStatsResponse, ProjectStatus
)
from app.services.dynamodb import DynamoDBService
from app.utils.auth import get_current_user
from app.utils.pagination import PaginationParams


router = APIRouter()
logger = structlog.get_logger()


def get_dynamodb_service() -> DynamoDBService:
    return DynamoDBService()


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: CreateProjectRequest,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Create a new project"""
    try:
        # Add user_id to project data
        project_dict = project_data.dict()
        project_dict['user_id'] = current_user['user_id']
        
        # Create project in database
        created_project = await db_service.create_project(project_dict)
        
        logger.info(
            "Project created successfully",
            project_id=created_project['project_id'],
            user_id=current_user['user_id']
        )
        
        return Project(**created_project)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create project", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Get project by ID"""
    try:
        project = await db_service.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if user has access to this project
        if project['user_id'] != current_user['user_id'] and current_user['user_id'] not in project.get('team_members', []):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return Project(**project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get project", project_id=project_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    update_data: UpdateProjectRequest,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Update project"""
    try:
        # First check if project exists and user has access
        existing_project = await db_service.get_project(project_id)
        
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if existing_project['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update project
        update_dict = update_data.dict(exclude_unset=True)
        updated_project = await db_service.update_project(project_id, update_dict)
        
        logger.info(
            "Project updated successfully",
            project_id=project_id,
            user_id=current_user['user_id']
        )
        
        return Project(**updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update project", project_id=project_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Delete project"""
    try:
        # First check if project exists and user has access
        existing_project = await db_service.get_project(project_id)
        
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if existing_project['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete project
        success = await db_service.delete_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        logger.info(
            "Project deleted successfully",
            project_id=project_id,
            user_id=current_user['user_id']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete project", project_id=project_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """List projects for the current user"""
    try:
        # Calculate pagination
        limit = page_size
        
        # For simplicity, we'll use scan with pagination
        # In production, you might want to implement proper cursor-based pagination
        result = await db_service.list_projects(
            user_id=current_user['user_id'],
            status=status.value if status else None,
            limit=limit
        )
        
        projects = [Project(**item) for item in result['items']]
        
        # Simple pagination calculation
        total = result['count']
        has_next = result.get('last_evaluated_key') is not None
        
        logger.info(
            "Projects listed",
            user_id=current_user['user_id'],
            count=len(projects),
            status=status
        )
        
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except Exception as e:
        logger.error("Failed to list projects", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary", response_model=ProjectStatsResponse)
async def get_project_stats(
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Get project statistics for the current user"""
    try:
        stats = await db_service.get_project_stats(user_id=current_user['user_id'])
        
        logger.info("Project stats retrieved", user_id=current_user['user_id'])
        
        return ProjectStatsResponse(**stats)
        
    except Exception as e:
        logger.error("Failed to get project stats", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/start", response_model=Project)
async def start_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Start a project (change status to active)"""
    try:
        # Get existing project
        existing_project = await db_service.get_project(project_id)
        
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if existing_project['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update status to active and set started_at
        from datetime import datetime
        update_data = {
            'status': ProjectStatus.ACTIVE.value,
            'started_at': datetime.utcnow()
        }
        
        updated_project = await db_service.update_project(project_id, update_data)
        
        logger.info(
            "Project started",
            project_id=project_id,
            user_id=current_user['user_id']
        )
        
        return Project(**updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start project", project_id=project_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/complete", response_model=Project)
async def complete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Complete a project (change status to completed)"""
    try:
        # Get existing project
        existing_project = await db_service.get_project(project_id)
        
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if existing_project['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update status to completed and set completed_at
        from datetime import datetime
        update_data = {
            'status': ProjectStatus.COMPLETED.value,
            'completed_at': datetime.utcnow(),
            'progress_percentage': 100.0
        }
        
        updated_project = await db_service.update_project(project_id, update_data)
        
        logger.info(
            "Project completed",
            project_id=project_id,
            user_id=current_user['user_id']
        )
        
        return Project(**updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to complete project", project_id=project_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
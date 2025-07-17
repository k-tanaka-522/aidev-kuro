from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.utils.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()


class Artifact(BaseModel):
    artifact_id: str
    name: str
    artifact_type: str
    project_id: str
    file_path: str
    file_size: int
    content_type: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    description: str = ""
    tags: List[str] = []


class CreateArtifactRequest(BaseModel):
    name: str
    artifact_type: str
    project_id: str
    description: str = ""
    tags: List[str] = []


@router.get("/", response_model=List[Artifact])
async def list_artifacts(
    project_id: Optional[str] = None,
    artifact_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List artifacts"""
    try:
        # Mock artifacts
        mock_artifacts = [
            Artifact(
                artifact_id="artifact_001",
                name="Requirements Document",
                artifact_type="document",
                project_id=project_id or "proj_001",
                file_path="s3://bucket/requirements.pdf",
                file_size=1024000,
                content_type="application/pdf",
                created_by=current_user["user_id"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                description="Project requirements specification",
                tags=["requirements", "specification"]
            ),
            Artifact(
                artifact_id="artifact_002",
                name="System Architecture",
                artifact_type="diagram",
                project_id=project_id or "proj_001",
                file_path="s3://bucket/architecture.png",
                file_size=512000,
                content_type="image/png",
                created_by="agent_arch_001",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                description="System architecture diagram",
                tags=["architecture", "design"]
            )
        ]
        
        if artifact_type:
            mock_artifacts = [a for a in mock_artifacts if a.artifact_type == artifact_type]
        
        return mock_artifacts
    except Exception as e:
        logger.error("Failed to list artifacts", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{artifact_id}", response_model=Artifact)
async def get_artifact(
    artifact_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get artifact by ID"""
    try:
        # Mock artifact retrieval
        mock_artifact = Artifact(
            artifact_id=artifact_id,
            name="Test Artifact",
            artifact_type="document",
            project_id="proj_001",
            file_path="s3://bucket/test.pdf",
            file_size=1024,
            content_type="application/pdf",
            created_by=current_user["user_id"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            description="Test artifact"
        )
        
        return mock_artifact
    except Exception as e:
        logger.error("Failed to get artifact", artifact_id=artifact_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Artifact)
async def create_artifact(
    artifact_data: CreateArtifactRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new artifact"""
    try:
        # Mock artifact creation
        artifact = Artifact(
            artifact_id=f"artifact_{hash(artifact_data.name) % 10000:04d}",
            name=artifact_data.name,
            artifact_type=artifact_data.artifact_type,
            project_id=artifact_data.project_id,
            file_path=f"s3://bucket/{artifact_data.name.lower().replace(' ', '_')}.pdf",
            file_size=1024,
            content_type="application/pdf",
            created_by=current_user["user_id"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            description=artifact_data.description,
            tags=artifact_data.tags
        )
        
        logger.info("Artifact created", artifact_id=artifact.artifact_id, name=artifact.name)
        
        return artifact
    except Exception as e:
        logger.error("Failed to create artifact", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
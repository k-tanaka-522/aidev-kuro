from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, Enum):
    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DATA_PIPELINE = "data_pipeline"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class ProjectComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ENTERPRISE = "enterprise"


class ProjectRequirement(BaseModel):
    id: str = Field(..., description="Requirement ID")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Requirement description")
    priority: str = Field(default="medium", description="Priority level")
    category: str = Field(default="functional", description="Requirement category")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectMetadata(BaseModel):
    tags: List[str] = Field(default_factory=list, description="Project tags")
    tech_stack: List[str] = Field(default_factory=list, description="Technology stack")
    target_audience: str = Field(default="", description="Target audience")
    business_goals: List[str] = Field(default_factory=list, description="Business goals")
    constraints: List[str] = Field(default_factory=list, description="Project constraints")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")


class Project(BaseModel):
    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: str = Field(default="", max_length=1000, description="Project description")
    user_id: str = Field(..., description="Owner user ID")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Project status")
    project_type: ProjectType = Field(default=ProjectType.WEB_APPLICATION, description="Project type")
    complexity: ProjectComplexity = Field(default=ProjectComplexity.MEDIUM, description="Project complexity")
    
    # Requirements and specifications
    requirements: List[ProjectRequirement] = Field(default_factory=list, description="Project requirements")
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata, description="Project metadata")
    
    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Project start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Project completion timestamp")
    deadline: Optional[datetime] = Field(None, description="Project deadline")
    
    # Progress tracking
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    total_tasks: int = Field(default=0, ge=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, ge=0, description="Number of completed tasks")
    
    # Agent assignments
    assigned_agents: List[str] = Field(default_factory=list, description="List of assigned agent IDs")
    active_agents: List[str] = Field(default_factory=list, description="List of currently active agent IDs")
    
    # Collaboration
    team_members: List[str] = Field(default_factory=list, description="List of team member user IDs")
    channels: List[str] = Field(default_factory=list, description="List of communication channel IDs")
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project-specific settings")
    
    # Repository information
    repository_url: Optional[str] = Field(None, description="Git repository URL")
    repository_branch: str = Field(default="main", description="Main branch name")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: str = Field(default="", max_length=1000, description="Project description")
    project_type: ProjectType = Field(default=ProjectType.WEB_APPLICATION, description="Project type")
    complexity: ProjectComplexity = Field(default=ProjectComplexity.MEDIUM, description="Project complexity")
    requirements: List[ProjectRequirement] = Field(default_factory=list, description="Initial requirements")
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata, description="Project metadata")
    deadline: Optional[datetime] = Field(None, description="Project deadline")
    team_members: List[str] = Field(default_factory=list, description="Team member user IDs")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    project_type: Optional[ProjectType] = Field(None, description="Project type")
    complexity: Optional[ProjectComplexity] = Field(None, description="Project complexity")
    requirements: Optional[List[ProjectRequirement]] = Field(None, description="Project requirements")
    metadata: Optional[ProjectMetadata] = Field(None, description="Project metadata")
    deadline: Optional[datetime] = Field(None, description="Project deadline")
    team_members: Optional[List[str]] = Field(None, description="Team member user IDs")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Progress percentage")


class ProjectListResponse(BaseModel):
    projects: List[Project]
    total: int
    page: int
    page_size: int
    has_next: bool


class ProjectStatsResponse(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    draft_projects: int
    total_tasks: int
    completed_tasks: int
    average_completion_rate: float
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
import structlog

from app.utils.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()


class Agent(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    status: str
    project_id: Optional[str] = None
    description: str = ""
    capabilities: List[str] = []


class CreateAgentRequest(BaseModel):
    name: str
    agent_type: str
    project_id: Optional[str] = None
    description: str = ""


@router.get("/", response_model=List[Agent])
async def list_agents(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List agents"""
    try:
        # Mock agents
        mock_agents = [
            Agent(
                agent_id="agent_pm_001",
                name="Project Manager Agent",
                agent_type="pm",
                status="active",
                project_id=project_id,
                description="AI-powered project management agent",
                capabilities=["project_planning", "task_management", "risk_assessment"]
            ),
            Agent(
                agent_id="agent_arch_001",
                name="Software Architect Agent",
                agent_type="architect",
                status="active",
                project_id=project_id,
                description="AI-powered software architecture agent",
                capabilities=["system_design", "technology_selection", "architecture_review"]
            ),
            Agent(
                agent_id="agent_sec_001",
                name="Security Agent",
                agent_type="security",
                status="active",
                project_id=project_id,
                description="AI-powered security analysis agent",
                capabilities=["security_review", "vulnerability_assessment", "compliance_check"]
            )
        ]
        
        return mock_agents
    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Agent)
async def create_agent(
    agent_data: CreateAgentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new agent"""
    try:
        # Mock agent creation
        agent = Agent(
            agent_id=f"agent_{agent_data.agent_type}_{hash(agent_data.name) % 1000:03d}",
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            status="active",
            project_id=agent_data.project_id,
            description=agent_data.description
        )
        
        logger.info("Agent created", agent_id=agent.agent_id, agent_type=agent.agent_type)
        
        return agent
    except Exception as e:
        logger.error("Failed to create agent", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get agent by ID"""
    try:
        # Mock agent retrieval
        mock_agent = Agent(
            agent_id=agent_id,
            name="Test Agent",
            agent_type="pm",
            status="active",
            description="Test agent description"
        )
        
        return mock_agent
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
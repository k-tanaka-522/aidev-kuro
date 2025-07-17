import json
import boto3
import logging
from typing import Dict, Any
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_agent = boto3.client('bedrock-agent-runtime')


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for PM Agent invocation
    """
    try:
        logger.info(f"PM Agent invoked with event: {json.dumps(event)}")
        
        # Extract request data
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        
        project_data = body.get('project_data', {})
        user_message = body.get('message', '')
        session_id = body.get('session_id', str(uuid.uuid4()))
        
        # Mock PM Agent response for now
        # In production, this would invoke Bedrock Agent
        response = generate_pm_response(project_data, user_message)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'agent_id': 'pm_agent_001',
                'agent_type': 'pm',
                'session_id': session_id,
                'response': response,
                'timestamp': '2024-01-01T00:00:00Z'
            })
        }
        
    except Exception as e:
        logger.error(f"Error in PM Agent: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def generate_pm_response(project_data: Dict[str, Any], user_message: str) -> Dict[str, Any]:
    """
    Generate PM agent response based on project data and user message
    """
    project_name = project_data.get('name', 'Unknown Project')
    project_type = project_data.get('project_type', 'web_application')
    
    # Mock response based on common PM scenarios
    if 'plan' in user_message.lower() or 'schedule' in user_message.lower():
        return {
            'message': f"I'll create a comprehensive project plan for '{project_name}'. Based on the {project_type} type, I recommend the following phases:",
            'artifacts': [
                {
                    'type': 'project_plan',
                    'title': 'Project Plan',
                    'content': {
                        'phases': [
                            {
                                'name': 'Requirements Analysis',
                                'duration': '1 week',
                                'tasks': ['Gather requirements', 'Stakeholder interviews', 'Create user stories']
                            },
                            {
                                'name': 'Design Phase',
                                'duration': '2 weeks', 
                                'tasks': ['System architecture', 'UI/UX design', 'Database design']
                            },
                            {
                                'name': 'Development',
                                'duration': '4 weeks',
                                'tasks': ['Frontend development', 'Backend development', 'Integration']
                            },
                            {
                                'name': 'Testing & Deployment',
                                'duration': '1 week',
                                'tasks': ['Unit testing', 'Integration testing', 'Deployment setup']
                            }
                        ],
                        'total_duration': '8 weeks',
                        'team_size': '3-5 developers'
                    }
                }
            ],
            'next_actions': [
                'Review and approve the project plan',
                'Assign team members to phases',
                'Set up project tracking tools'
            ]
        }
    
    elif 'risk' in user_message.lower():
        return {
            'message': f"I've identified potential risks for the {project_name} project:",
            'artifacts': [
                {
                    'type': 'risk_assessment',
                    'title': 'Risk Assessment',
                    'content': {
                        'high_risks': [
                            {
                                'risk': 'Scope creep',
                                'probability': 'High',
                                'impact': 'High',
                                'mitigation': 'Clear requirement documentation and change control process'
                            },
                            {
                                'risk': 'Technical complexity',
                                'probability': 'Medium',
                                'impact': 'High',
                                'mitigation': 'Proof of concept and technical spikes'
                            }
                        ],
                        'medium_risks': [
                            {
                                'risk': 'Resource availability',
                                'probability': 'Medium',
                                'impact': 'Medium',
                                'mitigation': 'Cross-training and backup resources'
                            }
                        ]
                    }
                }
            ],
            'next_actions': [
                'Implement risk mitigation strategies',
                'Set up regular risk review meetings',
                'Create contingency plans'
            ]
        }
    
    else:
        return {
            'message': f"Hello! I'm the PM Agent for '{project_name}'. I can help you with project planning, risk assessment, resource allocation, and progress tracking. What would you like to work on?",
            'capabilities': [
                'Project planning and scheduling',
                'Risk assessment and mitigation',
                'Resource allocation',
                'Progress tracking and reporting',
                'Stakeholder communication',
                'Change management'
            ],
            'suggested_actions': [
                'Create project plan',
                'Assess project risks',
                'Define team structure',
                'Set up project milestones'
            ]
        }


def invoke_bedrock_agent(agent_id: str, session_id: str, input_text: str) -> Dict[str, Any]:
    """
    Invoke Bedrock Agent (for production use)
    """
    try:
        response = bedrock_agent.invoke_agent(
            agentId=agent_id,
            agentAliasId='TSTALIASID',
            sessionId=session_id,
            inputText=input_text
        )
        
        # Process the response stream
        result = ''
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return {'message': result}
        
    except Exception as e:
        logger.error(f"Error invoking Bedrock Agent: {str(e)}")
        raise
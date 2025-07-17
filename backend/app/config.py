from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application settings
    app_name: str = "AgentDev Platform API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Environment
    environment: str = "dev"
    project_name: str = "agentdev"
    
    # AWS settings
    aws_region: str = "us-east-1"
    bedrock_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # DynamoDB tables
    projects_table: str = f"agentdev-dev-projects"
    agents_table: str = f"agentdev-dev-agents"
    messages_table: str = f"agentdev-dev-messages"
    tasks_table: str = f"agentdev-dev-tasks"
    channels_table: str = f"agentdev-dev-channels"
    artifacts_table: str = f"agentdev-dev-artifacts"
    ws_connections_table: str = f"agentdev-dev-ws-connections"
    
    # S3 buckets
    artifacts_bucket: str = f"agentdev-dev-artifacts"
    backup_bucket: str = f"agentdev-dev-backup"
    knowledge_base_bucket: str = f"agentdev-dev-knowledge-base"
    logs_bucket: str = f"agentdev-dev-logs"
    
    # Cognito settings
    user_pool_id: Optional[str] = None
    user_pool_client_id: Optional[str] = None
    user_pool_region: str = "us-east-1"
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "https://localhost:3000"]
    
    # WebSocket settings
    websocket_url: Optional[str] = None
    
    # Redis settings (for caching)
    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: list[str] = [
        "application/pdf",
        "text/plain",
        "application/json",
        "text/markdown",
        "application/zip",
        "image/png",
        "image/jpeg"
    ]
    
    # Bedrock settings
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    pm_agent_id: Optional[str] = None
    architect_agent_id: Optional[str] = None
    security_agent_id: Optional[str] = None
    
    # Monitoring settings
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    
    def get_table_name(self, table_type: str) -> str:
        """Get full table name with environment prefix"""
        return f"{self.project_name}-{self.environment}-{table_type}"
    
    def get_bucket_name(self, bucket_type: str) -> str:
        """Get full bucket name with environment prefix"""
        account_id = os.environ.get('AWS_ACCOUNT_ID', '123456789012')
        return f"{self.project_name}-{self.environment}-{bucket_type}-{account_id}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
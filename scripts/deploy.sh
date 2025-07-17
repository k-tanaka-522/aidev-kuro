#!/bin/bash

set -e  # Exit on any error

# Configuration
PROJECT_NAME="agentdev"
AWS_REGION="us-east-1"
BEDROCK_REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_success "All prerequisites met."
}

get_environment() {
    if [ -z "$1" ]; then
        echo "dev"
    else
        echo "$1"
    fi
}

validate_environment() {
    local env=$1
    if [[ "$env" != "dev" && "$env" != "staging" && "$env" != "production" ]]; then
        log_error "Invalid environment: $env. Must be 'dev', 'staging', or 'production'."
        exit 1
    fi
}

deploy_infrastructure() {
    local environment=$1
    log_info "Deploying infrastructure for environment: $environment"
    
    local stack_name="${PROJECT_NAME}-${environment}"
    
    # Deploy main CloudFormation stack
    aws cloudformation deploy \
        --template-file cloudformation/main.yaml \
        --stack-name "$stack_name" \
        --parameter-overrides \
            Environment="$environment" \
            ProjectName="$PROJECT_NAME" \
            BedrockRegion="$BEDROCK_REGION" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION" \
        --no-fail-on-empty-changeset
    
    if [ $? -eq 0 ]; then
        log_success "Infrastructure deployed successfully."
    else
        log_error "Infrastructure deployment failed."
        exit 1
    fi
}

build_and_push_images() {
    local environment=$1
    log_info "Building and pushing Docker images for environment: $environment"
    
    # Get AWS account ID
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ecr_registry"
    
    # Create ECR repositories if they don't exist
    aws ecr describe-repositories --repository-names "${PROJECT_NAME}-backend" --region "$AWS_REGION" 2>/dev/null || \
        aws ecr create-repository --repository-name "${PROJECT_NAME}-backend" --region "$AWS_REGION"
    
    aws ecr describe-repositories --repository-names "${PROJECT_NAME}-frontend" --region "$AWS_REGION" 2>/dev/null || \
        aws ecr create-repository --repository-name "${PROJECT_NAME}-frontend" --region "$AWS_REGION"
    
    # Build and push backend image
    log_info "Building backend image..."
    docker build -t "${PROJECT_NAME}-backend:latest" ./backend
    docker tag "${PROJECT_NAME}-backend:latest" "${ecr_registry}/${PROJECT_NAME}-backend:latest"
    docker tag "${PROJECT_NAME}-backend:latest" "${ecr_registry}/${PROJECT_NAME}-backend:${environment}"
    docker push "${ecr_registry}/${PROJECT_NAME}-backend:latest"
    docker push "${ecr_registry}/${PROJECT_NAME}-backend:${environment}"
    
    # Build frontend
    log_info "Building frontend..."
    cd frontend
    npm ci
    npm run build
    cd ..
    
    # Build and push frontend image
    log_info "Building frontend image..."
    docker build -t "${PROJECT_NAME}-frontend:latest" ./frontend
    docker tag "${PROJECT_NAME}-frontend:latest" "${ecr_registry}/${PROJECT_NAME}-frontend:latest"
    docker tag "${PROJECT_NAME}-frontend:latest" "${ecr_registry}/${PROJECT_NAME}-frontend:${environment}"
    docker push "${ecr_registry}/${PROJECT_NAME}-frontend:latest"
    docker push "${ecr_registry}/${PROJECT_NAME}-frontend:${environment}"
    
    log_success "Docker images built and pushed successfully."
}

deploy_lambda_functions() {
    local environment=$1
    log_info "Deploying Lambda functions for environment: $environment"
    
    # Package and deploy Lambda functions
    cd lambda/agents
    
    # Create deployment package
    zip -r pm_handler.zip pm_handler.py
    
    # Update Lambda function if it exists
    local function_name="${PROJECT_NAME}-${environment}-pm-agent-handler"
    
    if aws lambda get-function --function-name "$function_name" --region "$AWS_REGION" 2>/dev/null; then
        aws lambda update-function-code \
            --function-name "$function_name" \
            --zip-file fileb://pm_handler.zip \
            --region "$AWS_REGION"
    else
        log_warning "Lambda function $function_name not found. It will be created by CloudFormation."
    fi
    
    # Clean up
    rm -f pm_handler.zip
    cd ../..
    
    log_success "Lambda functions deployed successfully."
}

update_ecs_services() {
    local environment=$1
    log_info "Updating ECS services for environment: $environment"
    
    # Get cluster name
    local cluster_name=$(aws ecs list-clusters \
        --query "clusterArns[?contains(@, '${PROJECT_NAME}-${environment}')]" \
        --output text --region "$AWS_REGION" | cut -d'/' -f2)
    
    if [ -n "$cluster_name" ]; then
        # Get service names
        local services=$(aws ecs list-services \
            --cluster "$cluster_name" \
            --query "serviceArns" \
            --output text --region "$AWS_REGION")
        
        for service_arn in $services; do
            local service_name=$(echo "$service_arn" | cut -d'/' -f3)
            log_info "Updating service: $service_name"
            
            aws ecs update-service \
                --cluster "$cluster_name" \
                --service "$service_name" \
                --force-new-deployment \
                --region "$AWS_REGION"
        done
        
        # Wait for services to be stable
        log_info "Waiting for services to stabilize..."
        aws ecs wait services-stable \
            --cluster "$cluster_name" \
            --services $(echo "$services" | tr ' ' '\n' | cut -d'/' -f3 | tr '\n' ' ') \
            --region "$AWS_REGION"
        
        log_success "ECS services updated successfully."
    else
        log_warning "No ECS cluster found for environment: $environment"
    fi
}

run_smoke_tests() {
    local environment=$1
    log_info "Running smoke tests for environment: $environment"
    
    # Get ALB DNS name
    local alb_dns=$(aws elbv2 describe-load-balancers \
        --names "${PROJECT_NAME}-${environment}-alb" \
        --query 'LoadBalancers[0].DNSName' \
        --output text --region "$AWS_REGION" 2>/dev/null)
    
    if [ "$alb_dns" != "None" ] && [ -n "$alb_dns" ]; then
        local base_url="https://$alb_dns"
        
        # Test health endpoint
        log_info "Testing health endpoint..."
        if curl -f -s "$base_url/health" > /dev/null; then
            log_success "Health check passed."
        else
            log_error "Health check failed."
            return 1
        fi
        
        # Test API endpoint
        log_info "Testing API endpoint..."
        if curl -f -s "$base_url/api/v1/projects/" > /dev/null; then
            log_success "API endpoint check passed."
        else
            log_warning "API endpoint check failed (might need authentication)."
        fi
        
        log_success "Smoke tests completed."
    else
        log_warning "Load balancer not found. Skipping smoke tests."
    fi
}

setup_knowledge_base() {
    local environment=$1
    log_info "Setting up knowledge base for environment: $environment"
    
    # Get S3 bucket name
    local bucket_name="${PROJECT_NAME}-${environment}-knowledge-base-$(aws sts get-caller-identity --query Account --output text)"
    
    # Upload knowledge base documents
    if [ -d "knowledge-base" ]; then
        aws s3 sync knowledge-base/ "s3://$bucket_name/knowledge-base/" --region "$AWS_REGION"
        log_success "Knowledge base documents uploaded."
    else
        log_warning "Knowledge base directory not found. Skipping upload."
    fi
}

cleanup_old_images() {
    local environment=$1
    log_info "Cleaning up old Docker images for environment: $environment"
    
    # Keep only the latest 5 images for each repository
    for repo in "${PROJECT_NAME}-backend" "${PROJECT_NAME}-frontend"; do
        aws ecr describe-images \
            --repository-name "$repo" \
            --query 'sort_by(imageDetails,&imagePushedAt)[:-5].[imageDigest]' \
            --output text --region "$AWS_REGION" | \
        while read digest; do
            if [ ! -z "$digest" ] && [ "$digest" != "None" ]; then
                aws ecr batch-delete-image \
                    --repository-name "$repo" \
                    --image-ids imageDigest="$digest" \
                    --region "$AWS_REGION" > /dev/null
            fi
        done
    done
    
    log_success "Old Docker images cleaned up."
}

main() {
    log_info "Starting deployment script for AgentDev Platform"
    
    # Parse arguments
    local environment=$(get_environment "$1")
    local skip_build=false
    local skip_tests=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                skip_build=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [environment] [options]"
                echo "Environments: dev, staging, production"
                echo "Options:"
                echo "  --skip-build    Skip building and pushing Docker images"
                echo "  --skip-tests    Skip running smoke tests"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                environment="$1"
                shift
                ;;
        esac
    done
    
    validate_environment "$environment"
    check_prerequisites
    
    log_info "Deploying to environment: $environment"
    
    # Deploy infrastructure
    deploy_infrastructure "$environment"
    
    # Build and push images (unless skipped)
    if [ "$skip_build" = false ]; then
        build_and_push_images "$environment"
    else
        log_info "Skipping Docker image build (--skip-build specified)."
    fi
    
    # Deploy Lambda functions
    deploy_lambda_functions "$environment"
    
    # Update ECS services
    update_ecs_services "$environment"
    
    # Setup knowledge base
    setup_knowledge_base "$environment"
    
    # Run smoke tests (unless skipped)
    if [ "$skip_tests" = false ]; then
        # Wait a bit for services to be ready
        sleep 30
        run_smoke_tests "$environment"
    else
        log_info "Skipping smoke tests (--skip-tests specified)."
    fi
    
    # Cleanup old images
    cleanup_old_images "$environment"
    
    log_success "Deployment completed successfully for environment: $environment"
    
    # Output useful information
    echo ""
    echo "=== Deployment Summary ==="
    echo "Environment: $environment"
    echo "Region: $AWS_REGION"
    echo "Project: $PROJECT_NAME"
    echo ""
    
    # Get ALB DNS
    local alb_dns=$(aws elbv2 describe-load-balancers \
        --names "${PROJECT_NAME}-${environment}-alb" \
        --query 'LoadBalancers[0].DNSName' \
        --output text --region "$AWS_REGION" 2>/dev/null)
    
    if [ "$alb_dns" != "None" ] && [ -n "$alb_dns" ]; then
        echo "Application URL: https://$alb_dns"
        echo "API URL: https://$alb_dns/api/v1/"
        echo "Health Check: https://$alb_dns/health"
    fi
    
    echo ""
    echo "To monitor the deployment:"
    echo "aws ecs describe-services --cluster ${PROJECT_NAME}-${environment} --region $AWS_REGION"
    echo ""
}

# Run main function with all arguments
main "$@"
#!/bin/bash

set -e  # Exit on any error

# Configuration
PROJECT_NAME="agentdev"
NODE_VERSION="18"
PYTHON_VERSION="3.11"

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

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 is installed."
        return 0
    else
        log_error "$1 is not installed."
        return 1
    fi
}

install_node() {
    log_info "Installing Node.js $NODE_VERSION..."
    
    if command -v node &> /dev/null; then
        local current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$current_version" -ge "$NODE_VERSION" ]; then
            log_success "Node.js $current_version is already installed and meets requirements."
            return 0
        fi
    fi
    
    # Install Node.js using NodeSource repository (for Ubuntu/Debian)
    if command -v apt-get &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_${NODE_VERSION}.x | sudo bash -
        sudo yum install -y nodejs
    elif command -v brew &> /dev/null; then
        brew install node@${NODE_VERSION}
    else
        log_error "Unable to install Node.js automatically. Please install manually."
        return 1
    fi
    
    log_success "Node.js installed successfully."
}

install_python() {
    log_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        local current_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$current_version" = "3.11" ] || [ "$current_version" = "3.12" ]; then
            log_success "Python $current_version is already installed and meets requirements."
            return 0
        fi
    fi
    
    # Install Python (for Ubuntu/Debian)
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3.11 python3.11-pip python3.11-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python311 python311-pip
    elif command -v brew &> /dev/null; then
        brew install python@3.11
    else
        log_error "Unable to install Python automatically. Please install Python $PYTHON_VERSION manually."
        return 1
    fi
    
    log_success "Python installed successfully."
}

install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker is already installed."
        return 0
    fi
    
    # Install Docker (for Ubuntu/Debian)
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        
        echo \
          "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
          sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
          
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        
    elif command -v yum &> /dev/null; then
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
        
    elif command -v brew &> /dev/null; then
        brew install --cask docker
        
    else
        log_error "Unable to install Docker automatically. Please install manually."
        return 1
    fi
    
    log_success "Docker installed successfully."
    log_warning "You may need to log out and back in for Docker group membership to take effect."
}

install_aws_cli() {
    log_info "Installing AWS CLI..."
    
    if command -v aws &> /dev/null; then
        local current_version=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2 | cut -d'.' -f1)
        if [ "$current_version" -ge "2" ]; then
            log_success "AWS CLI v2 is already installed."
            return 0
        fi
    fi
    
    # Install AWS CLI v2
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf awscliv2.zip aws/
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        log_error "Unsupported OS for automatic AWS CLI installation."
        return 1
    fi
    
    log_success "AWS CLI installed successfully."
}

setup_backend() {
    log_info "Setting up backend environment..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy
    
    cd ..
    
    log_success "Backend environment set up successfully."
}

setup_frontend() {
    log_info "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    npm ci
    
    cd ..
    
    log_success "Frontend environment set up successfully."
}

setup_e2e_tests() {
    log_info "Setting up E2E tests environment..."
    
    cd e2e-tests
    
    # Install dependencies
    npm ci
    
    # Install Playwright browsers
    npx playwright install
    
    cd ..
    
    log_success "E2E tests environment set up successfully."
}

create_env_files() {
    log_info "Creating environment configuration files..."
    
    # Backend .env file
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# Development environment settings
DEBUG=true
ENVIRONMENT=dev
PROJECT_NAME=agentdev

# AWS settings
AWS_REGION=us-east-1
BEDROCK_REGION=us-east-1

# Database settings (use local DynamoDB for development)
AWS_ENDPOINT_URL=http://localhost:8000

# API settings
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]

# JWT settings
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File upload settings
MAX_FILE_SIZE=104857600
EOF
        log_success "Created backend/.env file."
    else
        log_info "Backend .env file already exists."
    fi
    
    # Frontend .env file
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
# Development environment settings
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
EOF
        log_success "Created frontend/.env file."
    else
        log_info "Frontend .env file already exists."
    fi
    
    # E2E tests .env file
    if [ ! -f "e2e-tests/.env" ]; then
        cp e2e-tests/.env.example e2e-tests/.env
        log_success "Created e2e-tests/.env file."
    else
        log_info "E2E tests .env file already exists."
    fi
}

setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "Running pre-commit checks..."

# Check backend code formatting
echo "Checking backend code formatting..."
cd backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    black --check . || exit 1
    flake8 . || exit 1
fi
cd ..

# Check frontend code formatting
echo "Checking frontend code formatting..."
cd frontend
npm run lint || exit 1
cd ..

echo "Pre-commit checks passed!"
EOF
    
    chmod +x .git/hooks/pre-commit
    log_success "Git pre-commit hook installed."
}

run_initial_tests() {
    log_info "Running initial tests to verify setup..."
    
    # Test backend
    log_info "Testing backend setup..."
    cd backend
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python -c "import app.main; print('Backend imports working!')"
    fi
    cd ..
    
    # Test frontend build
    log_info "Testing frontend setup..."
    cd frontend
    npm run type-check
    cd ..
    
    log_success "Initial tests passed!"
}

display_next_steps() {
    log_success "Setup completed successfully!"
    
    echo ""
    echo "=== Next Steps ==="
    echo ""
    echo "1. Configure AWS credentials:"
    echo "   aws configure"
    echo ""
    echo "2. Start the development servers:"
    echo "   # Terminal 1 - Backend"
    echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
    echo "   # Terminal 2 - Frontend"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "3. Run tests:"
    echo "   # Backend tests"
    echo "   cd backend && source venv/bin/activate && pytest"
    echo ""
    echo "   # Frontend tests"
    echo "   cd frontend && npm test"
    echo ""
    echo "   # E2E tests"
    echo "   cd e2e-tests && npm test"
    echo ""
    echo "4. Deploy to AWS:"
    echo "   ./scripts/deploy.sh dev"
    echo ""
    echo "Application URLs (when running locally):"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo ""
}

main() {
    log_info "Setting up AgentDev Platform development environment"
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        log_error "Please run this script from the project root directory."
        exit 1
    fi
    
    # Install system dependencies
    log_info "Installing system dependencies..."
    
    install_node
    install_python
    install_docker
    install_aws_cli
    
    # Setup project environments
    setup_backend
    setup_frontend
    setup_e2e_tests
    
    # Create configuration files
    create_env_files
    
    # Setup Git hooks
    setup_git_hooks
    
    # Run initial tests
    run_initial_tests
    
    # Display next steps
    display_next_steps
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "This script sets up the development environment for AgentDev Platform."
            echo "It will install required dependencies and configure the project."
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main
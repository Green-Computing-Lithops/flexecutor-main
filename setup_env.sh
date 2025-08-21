#!/bin/bash
# FlexExecutor Environment Setup Script
# This script loads environment variables from .env file and validates AWS credentials

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to load .env file
load_env_file() {
    local env_file="${1:-.env}"
    
    if [[ ! -f "$env_file" ]]; then
        print_error "$env_file not found!"
        print_status "Please create $env_file from .env.example:"
        echo "  cp .env.example .env"
        echo "  # Edit .env with your actual credentials"
        return 1
    fi
    
    print_status "Loading environment variables from $env_file..."
    
    # Load environment variables, skipping comments and empty lines
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Export the variable
        if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # Remove surrounding quotes if present
            if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
                value="${BASH_REMATCH[1]}"
            fi
            
            export "$key"="$value"
        fi
    done < "$env_file"
    
    print_success "Environment variables loaded successfully"
}

# Function to validate AWS credentials
validate_aws_credentials() {
    print_status "Validating AWS credentials..."
    
    local required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY")
    local missing_vars=()
    local placeholder_vars=()
    
    # Check required variables
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"_here" ]]; then
            placeholder_vars+=("$var")
        fi
    done
    
    # Report missing variables
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    # Report placeholder variables
    if [[ ${#placeholder_vars[@]} -gt 0 ]]; then
        print_error "Please replace placeholder values for:"
        for var in "${placeholder_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    # Check optional variables for placeholders
    local optional_vars=("AWS_SESSION_TOKEN" "AWS_DEFAULT_REGION")
    for var in "${optional_vars[@]}"; do
        if [[ -n "${!var}" && "${!var}" == *"_here" ]]; then
            print_warning "$var appears to have a placeholder value: ${!var}"
        fi
    done
    
    print_success "AWS credentials validation passed"
    return 0
}

# Function to print environment status
print_env_status() {
    echo
    echo "=== Environment Variables Status ==="
    echo
    
    # AWS Configuration
    echo "AWS Configuration:"
    local aws_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_SESSION_TOKEN" "AWS_DEFAULT_REGION")
    
    for var in "${aws_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            case "$var" in
                "AWS_ACCESS_KEY_ID"|"AWS_SECRET_ACCESS_KEY"|"AWS_SESSION_TOKEN")
                    # Mask sensitive values
                    local value="${!var}"
                    if [[ ${#value} -gt 12 ]]; then
                        local masked="${value:0:8}...${value: -4}"
                    else
                        local masked="***"
                    fi
                    echo "  $var: $masked"
                    ;;
                *)
                    echo "  $var: ${!var}"
                    ;;
            esac
        else
            echo "  $var: Not set"
        fi
    done
    
    echo
    echo "Other Configuration:"
    local other_vars=("LITHOPS_CONFIG_FILE" "DOCKER_ENGINE")
    
    for var in "${other_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            echo "  $var: ${!var}"
        else
            echo "  $var: Not set"
        fi
    done
}

# Function to activate virtual environment if it exists
activate_venv() {
    local venv_paths=("venv310/bin/activate" "venv/bin/activate" "env/bin/activate")
    
    for venv_path in "${venv_paths[@]}"; do
        if [[ -f "$venv_path" ]]; then
            print_status "Activating virtual environment: $venv_path"
            source "$venv_path"
            print_success "Virtual environment activated"
            return 0
        fi
    done
    
    print_warning "No virtual environment found. Consider creating one:"
    echo "  python -m venv venv310"
    echo "  source venv310/bin/activate"
    echo "  pip install -r requirements.txt"
}

# Main function
main() {
    echo "FlexExecutor Environment Setup"
    echo "=============================="
    echo
    
    # Load environment variables
    if ! load_env_file; then
        exit 1
    fi
    
    # Validate AWS credentials
    if ! validate_aws_credentials; then
        print_error "AWS credentials validation failed!"
        print_status "Please check your .env file and ensure all required credentials are set."
        exit 1
    fi
    
    # Print environment status
    print_env_status
    
    # Try to activate virtual environment
    activate_venv
    
    echo
    print_success "Environment setup complete!"
    print_status "You can now run your FlexExecutor applications."
    echo
    print_status "Example usage:"
    echo "  python examples/montecarlo_pi_estimation/main.py"
    echo "  python examples/titanic/main.py"
    echo "  python examples/video/main.py"
    echo
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed
    main "$@"
else
    # Script is being sourced
    print_status "Script is being sourced. Loading environment variables..."
    load_env_file
    if validate_aws_credentials; then
        print_success "Environment variables loaded and validated successfully"
    else
        print_error "Environment validation failed"
        return 1
    fi
fi

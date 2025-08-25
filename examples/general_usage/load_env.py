#!/usr/bin/env python3
"""
Environment Variable Loader for FlexExecutor
This utility helps load environment variables from .env file and validates AWS credentials.
"""

import os
import sys
from pathlib import Path


def load_env_file(env_file_path=".env"):
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path (str): Path to the .env file
        
    Returns:
        dict: Dictionary of loaded environment variables
    """
    env_vars = {}
    env_path = Path(env_file_path)
    
    if not env_path.exists():
        print(f"Warning: {env_file_path} not found. Please create it from .env.example")
        return env_vars
    
    try:
        with open(env_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    os.environ[key] = value
                else:
                    print(f"Warning: Invalid line format at line {line_num}: {line}")
    
    except Exception as e:
        print(f"Error reading {env_file_path}: {e}")
        return {}
    
    return env_vars


def validate_aws_credentials():
    """
    Validate that required AWS credentials are set.
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    optional_vars = ['AWS_SESSION_TOKEN', 'AWS_DEFAULT_REGION']
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['your_aws_access_key_here', 'your_aws_secret_access_key_here']:
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    if placeholder_vars:
        print(f"Error: Please replace placeholder values for: {', '.join(placeholder_vars)}")
        return False
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value and value.endswith('_here'):
            print(f"Warning: {var} appears to have a placeholder value: {value}")
    
    print("✓ AWS credentials validation passed")
    return True


def print_env_status():
    """Print the status of environment variables."""
    print("\n=== Environment Variables Status ===")
    
    # AWS credentials
    aws_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_DEFAULT_REGION']
    print("\nAWS Configuration:")
    for var in aws_vars:
        value = os.getenv(var)
        if value:
            if var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
                # Mask sensitive values
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: Not set")
    
    # Other configuration
    other_vars = ['LITHOPS_CONFIG_FILE', 'DOCKER_ENGINE']
    print("\nOther Configuration:")
    for var in other_vars:
        value = os.getenv(var)
        print(f"  {var}: {value if value else 'Not set'}")


def main():
    """Main function to load and validate environment variables."""
    print("FlexExecutor Environment Loader")
    print("=" * 40)
    
    # Load environment variables
    env_vars = load_env_file()
    
    if env_vars:
        print(f"✓ Loaded {len(env_vars)} environment variables from .env")
    else:
        print("No environment variables loaded from .env file")
    
    # Validate AWS credentials
    if not validate_aws_credentials():
        print("\n❌ AWS credentials validation failed!")
        print("Please check your .env file and ensure all required credentials are set.")
        sys.exit(1)
    
    # Print status
    print_env_status()
    
    print("\n✅ Environment setup complete!")
    print("You can now run your FlexExecutor applications.")


if __name__ == "__main__":
    main()

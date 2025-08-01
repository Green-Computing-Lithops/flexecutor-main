#!/bin/bash

# Script to build ARM64 runtime for Titanic project
# This script will update credentials from aws_credentials.md and build the runtime

echo "Building ARM64 runtime for Titanic project..."

# Source the virtual environment
source venv310/bin/activate

# Extract credentials from aws_credentials.md
AWS_ACCESS_KEY_ID=$(grep 'export AWS_ACCESS_KEY_ID=' aws_credentials.md | cut -d'"' -f2)
AWS_SECRET_ACCESS_KEY=$(grep 'export AWS_SECRET_ACCESS_KEY=' aws_credentials.md | cut -d'"' -f2)
AWS_SESSION_TOKEN=$(grep 'export AWS_SESSION_TOKEN=' aws_credentials.md | cut -d'"' -f2)

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_SESSION_TOKEN" ]; then
    echo "Error: Could not extract AWS credentials from aws_credentials.md"
    echo "Please ensure the file contains valid credentials in the expected format."
    exit 1
fi

echo "Found AWS credentials, proceeding with runtime build..."

# Set environment variables
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"
export LITHOPS_CONFIG_FILE=config_aws.yaml

# Test credentials first
echo "Testing AWS credentials..."
aws sts get-caller-identity
if [ $? -ne 0 ]; then
    echo "Error: AWS credentials are invalid or expired."
    echo "Please update aws_credentials.md with fresh credentials from:"
    echo "https://cloudlab-urv.awsapps.com/start/#"
    exit 1
fi

echo "AWS credentials validated successfully!"

# Build the runtime
echo "Building ARM64 runtime: titanic_aws_lambda_arm"
lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm

if [ $? -eq 0 ]; then
    echo "✅ ARM64 runtime 'titanic_aws_lambda_arm' built successfully!"
    echo ""
    echo "You can now use this runtime in your Lithops configuration:"
    echo "runtime: titanic_aws_lambda_arm"
    echo "architecture: arm64"
else
    echo "❌ Runtime build failed. Please check the error messages above."
    exit 1
fi

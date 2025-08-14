

give me the list of the 4 commands to build each runtime example, the other 4 for running it and also all the command needed to install all the dependencies locally

Here are all the commands needed to build, run, and set up the runtime examples:

## Local Dependencies Installation Commands:

```bash
# Install libomp for ML example (macOS)
brew install libomp

# Install python-tk for Video example (macOS)
brew install python-tk@3.10

# Activate virtual environment
source venv310/bin/activate

# Set AWS credentials (replace with current credentials)
export AWS_ACCESS_KEY_ID="ASIA4MTWMECOLPTZCZ3G"
export AWS_SECRET_ACCESS_KEY="g8g6e0lWUH5AMgpguQpuCdYdYy6jcnYFkk2S459r"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjELf//////////wEaCXVzLWVhc3QtMSJHMEUCIQCzzGx5WBn4fqhLPhTwRkxygraIoicqtSnyGz+x94FrmwIgQyft/3lgUoDmNbzggkfh1tG9NVcOFLiu8+mwKXleF2Qq/wII8P//////////ARAAGgw4NTE3MjU1MjUxNDgiDLGC12ckyB6SdHWJOSrTAju7AcczMc7vZT+Qwzh53XGp8Lba1nvqVZ07wcKYJJNqrqCbTugZMU6PK76R8lgEebV5XjDgTSzpGD73oj0hjLuUd2q+9Era5mMIj9ZWfNQAOlELvBZ7KxC2dM1mArmCjbGe3Jc1xlFEfW0OyT4kCmRQOLlqn8un5SlVknlwTVujLVNRhyIBEGa+4rJtsO7nVE0WQjXD0vHOS1d7C5Sxd2m42JykA7iLFJ5s1gXoE79TyYhGh/6BXWRFaQ/IChlTsAmHipLhSeUSFUjbexlzd8Z5g7K7i6aejQTmFSQwWM/xYDEs+5Xdnwg6eFMw6oF74pie0cHO+wB4PrrYkZ73W2yCCespxHfc2th/wrXrZxqZm+P1yHjahl/z9BGc9rJexSqeCJfLsT/PSH5Glmyfit7re5CMbENO3Kblx6YKh0ei6nqBY5QIKuuD8ijiDBUkk5h01TDc/ufEBjqnAdTpi9K20Dn6gjvA1m1PyAaIK1agLn6IN4KO1wV59nCYUBgZfDdaAX9hOAjsNrJyjg9HxB3RCZ7h8WRUOUuBR0MJ1tplVGnIfMizb7lZ7wEAqxUdKD/J/L77Nvtgf+jVk1oNqIMoprh2bRXuH2uTEJVV312GXXJCYoTYPZp+TMWOJ6O671dw+88RSoN55Gjbdry5oXKADjHyctfPKcUCDAW81jhqPGui"

# Set environment variables for local dependencies
export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"
export PYTHONPATH="/opt/homebrew/Cellar/python-tk@3.10/3.10.18/lib/python3.10/site-packages:$PYTHONPATH"

# Set Lithops configuration
export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml
export DOCKER_ENGINE=podman

# Sync lithops fork
rm -rf lithops_fork && rsync -av --exclude='.git' /Users/arriazui/Desktop/GreenComputing/lithops_fork/ ./lithops_fork/
```

## Runtime Build Commands:

```bash
# 1. Build Titanic Runtime
lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm_greencomp_v1

# 2. Build ML Runtime
lithops runtime build -b aws_lambda -f examples/ml/Dockerfile.arm64 ml_aws_lambda_arm_greencomp_v1

# 3. Build Video Runtime
lithops runtime build -b aws_lambda -f examples/video/Dockerfile.arm64 video_aws_lambda_arm_greencomp_v1

# 4. Build Montecarlo Runtime (if needed)
lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 montecarlo_aws_lambda_arm_greencomp_v1
```

## Runtime Execution Commands:

```bash
# 1. Run Titanic Example
cd examples/titanic && python main.py

# 2. Run ML Example
cd examples/ml && python main.py

# 3. Run Video Example
cd examples/video && python main.py

# 4. Run Montecarlo Example
cd examples/montecarlo_pi_estimation && python main.py
```

## Complete Setup Script:

```bash
#!/bin/bash
# Complete setup and execution script

# Activate environment and set credentials
source venv310/bin/activate
export AWS_ACCESS_KEY_ID="ASIA4MTWMECOLPTZCZ3G"
export AWS_SECRET_ACCESS_KEY="g8g6e0lWUH5AMgpguQpuCdYdYy6jcnYFkk2S459r"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjELf//////////wEaCXVzLWVhc3QtMSJHMEUCIQCzzGx5WBn4fqhLPhTwRkxygraIoicqtSnyGz+x94FrmwIgQyft/3lgUoDmNbzggkfh1tG9NVcOFLiu8+mwKXleF2Qq/wII8P//////////ARAAGgw4NTE3MjU1MjUxNDgiDLGC12ckyB6SdHWJOSrTAju7AcczMc7vZT+Qwzh53XGp8Lba1nvqVZ07wcKYJJNqrqCbTugZMU6PK76R8lgEebV5XjDgTSzpGD73oj0hjLuUd2q+9Era5mMIj9ZWfNQAOlELvBZ7KxC2dM1mArmCjbGe3Jc1xlFEfW0OyT4kCmRQOLlqn8un5SlVknlwTVujLVNRhyIBEGa+4rJtsO7nVE0WQjXD0vHOS1d7C5Sxd2m42JykA7iLFJ5s1gXoE79TyYhGh/6BXWRFaQ/IChlTsAmHipLhSeUSFUjbexlzd8Z5g7K7i6aejQTmFSQwWM/xYDEs+5Xdnwg6eFMw6oF74pie0cHO+wB4PrrYkZ73W2yCCespxHfc2th/wrXrZxqZm+P1yHjahl/z9BGc9rJexSqeCJfLsT/PSH5Glmyfit7re5CMbENO3Kblx6YKh0ei6nqBY5QIKuuD8ijiDBUkk5h01TDc/ufEBjqnAdTpi9K20Dn6gjvA1m1PyAaIK1agLn6IN4KO1wV59nCYUBgZfDdaAX9hOAjsNrJyjg9HxB3RCZ7h8WRUOUuBR0MJ1tplVGnIfMizb7lZ7wEAqxUdKD/J/L77Nvtgf+jVk1oNqIMoprh2bRXuH2uTEJVV312GXXJCYoTYPZp+TMWOJ6O671dw+88RSoN55Gjbdry5oXKADjHyctfPKcUCDAW81jhqPGui"
export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml
export DOCKER_ENGINE=podman
export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"
export PYTHONPATH="/opt/homebrew/Cellar/python-tk@3.10/3.10.18/lib/python3.10/site-packages:$PYTHONPATH"

# Sync lithops fork
rm -rf lithops_fork && rsync -av --exclude='.git' /Users/arriazui/Desktop/GreenComputing/lithops_fork/ ./lithops_fork/

# Build all runtimes
echo "Building Titanic runtime..."
lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm_greencomp_v1

echo "Building ML runtime..."
lithops runtime build -b aws_lambda -f examples/ml/Dockerfile.arm64 ml_aws_lambda_arm_greencomp_v1

echo "Building Video runtime..."
lithops runtime build -b aws_lambda -f examples/video/Dockerfile.arm64 video_aws_lambda_arm_greencomp_v1

echo "All runtimes built successfully!"
```

## Additional Utility Commands:

```bash
# List all runtimes
lithops runtime list -b aws_lambda

# Delete a specific runtime
lithops runtime delete <runtime_name> -b aws_lambda

# Upload videos to S3 (if needed)
aws s3 cp test-bucket/videos/ s3://lithops-us-east-1-45dk/videos/ --recursive
```

**Note**: Remember to update the AWS credentials with current valid tokens before running these commands.
</result>
</attempt_completion>


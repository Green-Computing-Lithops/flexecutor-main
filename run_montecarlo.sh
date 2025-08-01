#!/bin/bash

# Navigate to flexecutor directory
cd /home/bigrobbin/Desktop/green_computing/flexecutor-main

# Activate virtual environment
source venv310/bin/activate

# Set AWS credentials
export AWS_ACCESS_KEY_ID="ASIA4MTWMECOH5W2MBKM"
export AWS_SECRET_ACCESS_KEY="+j+bhGkSBI0Px1f4jjvwaAD22Qkj1WJZvXbe9NUU"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEL///////////wEaCXVzLWVhc3QtMSJGMEQCIBHRbh4O5Cse81uwghddlBbGRFiuHXzFJdbvFf0jVN9ZAiAl7bPImme2IEb5Qhml6Y1e/YDDOuqaWv5shrtGxAU2Oyr/Agjn//////////8BEAAaDDg1MTcyNTUyNTE0OCIMRjkA3Rgu0hNfg/JkKtMCbqkPw9VNYrZTyRefBRn4//mNyoBqVGH6TI4wqwidt99JL0xzA9jyvUBIi0f0Pzt5x6FaLmEFSLj/DkQRZiX8+oQ2aZPaeUOD4Y/32KBWaTxzmU5irAHAv++ky7bvAEir46CJxwHlp7Q1FPlTnaWUVUgKoLWp3d8cGqs3mIyFHask1E9gbepiiYhNYxibtjV27NLPwJi3xkdaqabQ6jCU9a/6y5mrIxo2qJC9Ax3fS8iZR6WdLuhdeViVI+WO65My5AJI55YbhwNWHbvsuQpp3/vMH7rUgPMCUpEUdLl/a0a1zn52CkNT2vN5I3uu3fi1jmp32b2yY/EBuGWnbE/5SW2Qm6AkFnW7suJ2xPxrO9n0iJQkgnoAmdGSCN/56RUQe+Yodq7i4LJhR4I5NaKOFQbpTm8pXQhRda4u7EgCxLbcLGDxPaxdbZj69+rt60j6LEjVMO6xscQGOqgB8r3cOTABVIAcDjyGFwussdLQrJvibjcCtXXS6aI2q8vs8liHo2CyPxqGZqnaUMmDKoVAXvm1/p+FlTMLtkszHhmyeqkHNxwLbEUv4KMHztgHg8ZzMg1Hppbs28t/IbnktX7ZgvYOEzpvFG8miJujSVuBm1s1JMo3qSlnqaQHGUXXy9tmyvwils93NhvVOSI/HKUxduaMTFltpYz9yjnyQegrMQ2vTWoK"

# Set Lithops config file
export LITHOPS_CONFIG_FILE="/home/bigrobbin/Desktop/green_computing/flexecutor-main/config_aws.yaml"

echo "======================================================"
echo "Running Monte Carlo Pi Estimation with FlexExecutor"
echo "======================================================"
echo "Using virtual environment: $(which python)"
echo "Using Lithops config: $LITHOPS_CONFIG_FILE"
echo "AWS Region: us-east-1"
echo "======================================================"

# Run the Monte Carlo script
python examples/montecarlo_pi_estimation/main.py

echo "======================================================"
echo "Monte Carlo execution completed"
echo "======================================================"

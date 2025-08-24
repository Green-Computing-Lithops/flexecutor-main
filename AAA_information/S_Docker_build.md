# Clear any cached bucket environment variables
unset FLEX_BUCKET
unset LITHOPS_BUCKET

# Then run your script
python examples/montecarlo_pi_estimation/main.py



#!/bin/bash
# update_lithops_runtime.sh

# Set variables
NEW_VERSION="montecarlo_aws_lambda_arm_greencomp_v6"  # Increment this each time
FLEXECUTOR_DIR="REDACTED_SECRET_ACCESS_KEYlexecutor-main"

cd $FLEXECUTOR_DIR

# Step 0: Clean cache
echo "🧹 Cleaning cache..."
rm -rf ~/.lithops/cache/
rm -rf ~/.lithops/runtimes/
pip cache purge

# Step 1: Install updated lithops
echo "📦 Installing updated lithops fork..."
source venv310/bin/activate
pip uninstall lithops -y
cd lithops_fork && pip install -e . && cd ..

# Step 2: Set environment variables
export DOCKER_ENGINE=podman
export LITHOPS_CONFIG_FILE=$FLEXECUTOR_DIR/config_aws.yaml

# Step 3: Build runtime
echo "🔨 Building runtime: $NEW_VERSION"
lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 $NEW_VERSION

# Step 4: Update config
echo "⚙️ Updating configuration..."
sed -i '' "s/runtime: montecarlo_aws_lambda_arm_greencomp_v[0-9]*/runtime: $NEW_VERSION/g" config_aws.yaml

# Step 5: Test
echo "🚀 Testing new runtime..."
python examples/montecarlo_pi_estimation/main.py

echo "✅ Done! Check output for RAPL_wrong: [7, 7, 7, ...] to confirm new version."




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Done by you: 
export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYlexecutor-main/config_aws.yaml && source venv310/bin/activate && lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 montecarlo_aws_lambda_arm_greencomp_v3



export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYlexecutor-main/config_aws.yaml && source venv310/bin/activate && lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 montecarlo_aws_lambda_arm_greencomp_v4


```shell
source venv310/bin/activate && python examples/montecarlo_pi_estimation/main.py
```

🧹 __Step 0: Clean Cache and Previous Installations (IMPORTANT!)__
# Clean Lithops cache and metadata
rm -rf ~/.lithops/cache/
rm -rf ~/.lithops/runtimes/

# Clean local pip cache
pip cache purge

# Remove existing lithops installation from venv
source venv310/bin/activate
pip uninstall lithops -y


📦 __Step 1: Install Updated Lithops Fork in FlexExecutor Repository__
# Navigate to flexecutor-main directory
cd REDACTED_SECRET_ACCESS_KEYlexecutor-main

# Activate virtual environment
source venv310/bin/activate

# Sync the latest lithops_fork (if needed)
rm -rf lithops_fork && rsync -av --exclude='.git' REDACTED_SECRET_ACCESS_KEYithops_fork/ ./lithops_fork/

# Install the updated lithops fork in development mode
cd lithops_fork
pip install -e .
cd ..


🐳 __Step 2: Include Updated Version in Dockerfile/Runtime Image__
# This is already in examples/montecarlo_pi_estimation/Dockerfile.arm64
COPY lithops_fork/ /tmp/lithops_fork/
RUN cd /tmp/lithops_fork && pip install . && rm -rf /tmp/lithops_fork


🔨 __Step 3: Build the Runtime Image__
# Set environment variables
export DOCKER_ENGINE=podman
export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYlexecutor-main/config_aws.yaml

# Activate virtual environment
source venv310/bin/activate

# Build the runtime (increment version number: v4 -> v5, v6, etc.)
lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 montecarlo_aws_lambda_arm_greencomp_v5




☁️ __Step 4: Upload Runtime Version to AWS__
```javascript
Pushing runtime 851725525148.dkr.ecr.us-east-1.amazonaws.com/lithops_v361dev0_45dk/montecarlo_aws_lambda_arm_greencomp_v5:latest to AWS container registry
```


⚙️ __Step 5: Update Configuration to Use New Runtime__
⚙️ __Step 5: Update Configuration to Use New Runtime__
# Edit config_aws.yaml to use the new runtime version
# Change this line in config_aws.yaml:
# runtime: montecarlo_aws_lambda_arm_greencomp_v4
# To:
# runtime: montecarlo_aws_lambda_arm_greencomp_v5

🚀 __Step 6: Execute with New Version and Runtime__

# Activate virtual environment
source venv310/bin/activate

# Run your application (example with Monte Carlo)
python examples/montecarlo_pi_estimation/main.py


📝 __Complete One-Liner Script__
#!/bin/bash
# update_lithops_runtime.sh

# Set variables
NEW_VERSION="montecarlo_aws_lambda_arm_greencomp_v6"  # Increment this each time
FLEXECUTOR_DIR="REDACTED_SECRET_ACCESS_KEYlexecutor-main"

cd $FLEXECUTOR_DIR

# Step 0: Clean cache
echo "🧹 Cleaning cache..."
rm -rf ~/.lithops/cache/
rm -rf ~/.lithops/runtimes/
pip cache purge

# Step 1: Install updated lithops
echo "📦 Installing updated lithops fork..."
source venv310/bin/activate
pip uninstall lithops -y
cd lithops_fork && pip install -e . && cd ..

# Step 2: Set environment variables
export DOCKER_ENGINE=podman
export LITHOPS_CONFIG_FILE=$FLEXECUTOR_DIR/config_aws.yaml

# Step 3: Build runtime
echo "🔨 Building runtime: $NEW_VERSION"
lithops runtime build -b aws_lambda -f examples/montecarlo_pi_estimation/Dockerfile.arm64 $NEW_VERSION

# Step 4: Update config
echo "⚙️ Updating configuration..."
sed -i '' "s/runtime: montecarlo_aws_lambda_arm_greencomp_v[0-9]*/runtime: $NEW_VERSION/g" config_aws.yaml

# Step 5: Test
echo "🚀 Testing new runtime..."
python examples/montecarlo_pi_estimation/main.py

echo "✅ Done! Check output for RAPL_wrong: [7, 7, 7, ...] to confirm new version."

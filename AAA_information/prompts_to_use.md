# ENVIROMENT:
- Always use the venv310 activated 
source venv310/bin/activate

# CREDENTIALS
To actualize the credentials look at : 
- REDACTED_SECRET_ACCESS_KEYlexecutor-main/aws_credentials.md 

# PODMAN
Docker is not allowed, use Podman instead of docker, to build the runtime use always the lithops process, with something like this :
export DOCKER_ENGINE=podman && lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm_greencomp

# LITHOPS_CONFIG_FILE : 
export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYlexecutor-main/config_aws.yaml

The last version of lithops, actualized and always use and install should be : 
REDACTED_SECRET_ACCESS_KEYithops_fork 

# IMPORTANT: 
use this to create / manage runtimes : 
REDACTED_SECRET_ACCESS_KEYlexecutor-main/AAA_information/S_Docker_build.md

# With that in mind now INSTRUCTIONS: 
could you creaate a new runtime in base what i mention called titanic_aws_lambda_arm_greencomp_v1_512mb_v2 
where the runtime in aws is of 512Mb  for this file REDACTED_SECRET_ACCESS_KEYlexecutor-main/examples/titanic/main_batch_execution.py







 source venv310/bin/activate && export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID_HERE" && export DOCKER_ENGINE=docker && export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID_HERE" && export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY_HERE" && export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN_HERE" && export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYflexecutor-main/config_aws.yaml && python examples/video/main_batch_execution.py






 source venv310/bin/activate && export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID_HERE" && export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY_HERE" && export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN_HERE" && export LITHOPS_CONFIG_FILE=REDACTED_SECRET_ACCESS_KEYflexecutor-main/config_aws.yaml && python examples/titanic/main_batch_execution.py

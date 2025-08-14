cd /Users/arriazui/Desktop/GreenComputing/flexecutor-main && source venv310/bin/activate && rm -rf ~/.lithops/cache/ && rm -rf ~/.lithops/runtimes/

cd /Users/arriazui/Desktop/GreenComputing/flexecutor-main && source venv310/bin/activate && export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml && lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm_greencomp_v1_512mb_v2

# remove runtimes not used 
remove all other :
rm -rf ~/.lithops/cache/ && rm -rf ~/.lithops/runtimes/

rm -rf ~/.lithops/cache/

# commetns 
aws lambda list-functions --query 'Functions[?contains(FunctionName, `titanic`) || contains(FunctionName, `2048`)].{Name:FunctionName,Memory:MemorySize,Runtime:Runtime}' --output table 

aws lambda list-functions --query 'Functions[?contains(FunctionName, `titanic`)].{Name:FunctionName,Memory:MemorySize,Runtime:Runtime}' --output table

aws lambda list-functions --output table

cd /Users/arriazui/Desktop/GreenComputing/flexecutor-main && source venv310/bin/activate && export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml && python -c "
import lithops
from lithops_fork.lithops import config as lithops_config

# Force rebuild of the runtime
fexec = lithops.FunctionExecutor(runtime='titanic_aws_lambda_arm_greencomp_v1_2048mb', runtime_memory=2048)
print('Runtime configured successfully')
"
aws lambda get-function --function-name lithops-worker-45dk-361dev0-e0faabc9f7 --query 'Configuration.{Memory:MemorySize,Timeout:Timeout,Runtime:Runtime}' --output table







aws lambda list-functions --query 'Functions[?contains(FunctionName, `lithops-worker-45dk-361dev0`)].{Name:FunctionName,Memory:MemorySize}' --output json


lithops runtime build titanic_aws_lambda_arm_greencomp_v1_2048mb -b aws_lambda -f examples/titanic/Dockerfile.arm64
lithops runtime deploy titanic_aws_lambda_arm_greencomp_v1_2048mb -b aws_lambda --memory 2048


# ver todas las ejecuciones : 
lithops runtime list

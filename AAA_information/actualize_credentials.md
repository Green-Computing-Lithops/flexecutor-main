# The main description of the project is here : 
/path/to/flexecutor-main/AAA_information/cline_task_AWS_summarized.md

# ENVIROMENT:
- Always use the venv310 activated 
source venv310/bin/activate 

# CREDENTIALS
To actualize the credentials look at : 
- /path/to/flexecutor-main/aws_credentials.md 

# LITHOPS_CONFIG_FILE : 
export LITHOPS_CONFIG_FILE=/path/to/flexecutor-main/config_aws.yaml
* The last version of lithops, actualized and always use and install should be :  /path/to/lithops_fork 

# With that in mind now INSTRUCTIONS: 
1) Actualize the credeitials in config_aws.yaml in the /path/to/flexecutor-main/config_aws.yaml using the file : /path/to/flexecutor-main/aws_credentials.md

2) Run the ML : /path/to/flexecutor-main/examples/ml/main_batch_execution.py 
 
# The command for run should be like this : 
source venv310/bin/activate && export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=/path/to/flexecutor-main/config_aws.yaml && export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID_HERE" && export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY_HERE" && export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN_HERE" && python examples/video/main_batch_execution.py

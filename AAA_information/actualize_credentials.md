# The main description of the project is here : 
/Users/arriazui/Desktop/GreenComputing/flexecutor-main/AAA_information/cline_task_AWS_summarized.md

# ENVIROMENT:
- Always use the venv310 activated 
source venv310/bin/activate 

# CREDENTIALS
To actualize the credentials look at : 
- /Users/arriazui/Desktop/GreenComputing/flexecutor-main/aws_credentials.md 

# LITHOPS_CONFIG_FILE : 
export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml
* The last version of lithops, actualized and always use and install should be :  /Users/arriazui/Desktop/GreenComputing/lithops_fork 

# With that in mind now INSTRUCTIONS: 
1) Actualize the credeitials in config_aws.yaml in the /Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml using the file : /Users/arriazui/Desktop/GreenComputing/flexecutor-main/aws_credentials.md

2) Run: /Users/arriazui/Desktop/GreenComputing/flexecutor-main/examples/video/main_batch_execution.py 
and fix the error 

# The command for run should be like this : 
source venv310/bin/activate && export DOCKER_ENGINE=podman && export LITHOPS_CONFIG_FILE=/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml && export AWS_ACCESS_KEY_ID="ASIA4MTWMECOAU5H3IXX" && export AWS_SECRET_ACCESS_KEY="0rghKB6jCVeUdr8TJ0wbtA5kr70jPowAV0g6HQhB" && export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEF0aCXVzLWVhc3QtMSJHMEUCID/7+kIExthhWv1s5s0LxuuZwfABSMOP6T3rroxB51UwAiEA+3E0r8d6P5Ut8xMtDh6apKXlCKp0oXwaE2hgXoGJATcq/wIIpv//////////ARAAGgw4NTE3MjU1MjUxNDgiDADUShP8aEuFeLVI/SrTAhBPtySt9ydFghUbpBqBj+bKSAqDKEk3bjGjmPAer1i8oUYGbLarASBQZZ5rJxkAATVW8WzPutDMmI6Xb+35OsVma4G+ELNRYuRKwlHhhK0eUOMTXShSM7/0CcUOYJEz8mz0Oy0VuyuKCNd9yjysvCDOWTSdwJS3jmGhJ5HKRc+dFgNw/jFT1VqhQZ+lkHO795zWjxwcCK+KHCUm/6U7FRWcpCmbbyGnODm2nDSGqTNXkLpMEYTepRcmn/JbNPGFt88FdJvOb49qjxVYLERF+faCh6CTXSmkcntNkI0EoPLR9+Ke7494T5x6H0U0QtQuj4JRYrxZXRTzJQIibSC9QBsD7X3Z67YNr2yeLzHCUZgt4pLRJPz5tA5IjVdXtwYlLjYgx2WaYkFM9mnoOTaUUt5l9pn5rxXfHTRUsywExkT8K/df4yjqL5FSLYEE/U9SERrvJzC4yIzFBjqnAcXirr/vPYSWTm9Dh8UeSfvbx/BeaFydHCe6zUUMS+eV6a8jTgHxxYgVaeBDpu/Vyz1pfvPs78gjEDvn+0A7nnJJdwVM5v2aVxAsOBdPs+CYUiNphT2Wns+a3PMwLfYi2fbBrFEVeDHqGK5kEJ1N2gU2iVQuZzNDJUNOifo/igRZy7UssmG1lSviMXIu2D+5KqHLDRtfSGk+ZoWchmdJZ1PpJInXWuu5" && python examples/video/main_batch_execution.py



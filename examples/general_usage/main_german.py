import lithops
from lithops.storage import Storage

def funcion_german(x):
    storage = Storage()
    print(storage.list_keys("lithops-us-east-1-45dk"))
    return x + 1

executor = lithops.FunctionExecutor(config_file='/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml', log_level='debug')
ft = executor.map(funcion_german, [1, 2, 3])
print(executor.get_result(ft))

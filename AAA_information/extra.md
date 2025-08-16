source venv310/bin/activate && export LITHOPS_CONFIG_FILE="/home/minirobbin/Desktop/GreenComputing/flexecutor-main/config_aws.yaml" && python -c "
import sys
import os
sys.path.insert(0, os.path.abspath('lithops_fork'))
from lithops import FunctionExecutor
try:
    executor = FunctionExecutor()
    print('Current backend:', executor.backend)
    print('Current config:', executor.config)
    if hasattr(executor, 'compute_handler'):
        print('Compute handler:', executor.compute_handler)
        if hasattr(executor.compute_handler, 'list_runtimes'):
            print('Available runtimes:')
            runtimes = executor.compute_handler.list_runtimes()
            for runtime in runtimes:
                print(f'  - {runtime}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"
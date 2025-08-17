#!/usr/bin/env python3
"""
Simple test script to verify the ML runtime dependencies
"""
import sys
import os

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lithops_fork')))

from lithops import FunctionExecutor

def test_ml_dependencies():
    """Test function to verify ML dependencies are available"""
    try:
        import lightgbm
        import joblib
        import sklearn
        import numpy as np
        import scipy
        
        print("✓ All ML dependencies are available:")
        print(f"  - LightGBM: {lightgbm.__version__}")
        print(f"  - Joblib: {joblib.__version__}")
        print(f"  - Scikit-learn: {sklearn.__version__}")
        print(f"  - NumPy: {np.__version__}")
        print(f"  - SciPy: {scipy.__version__}")
        
        # Simple computation test
        data = np.array([[1, 2], [3, 4], [5, 6]])
        result = np.mean(data)
        print(f"  - NumPy computation test: mean = {result}")
        
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

if __name__ == "__main__":
    print("Testing ML runtime dependencies...")
    
    # Test locally first
    print("\n1. Testing local dependencies:")
    local_success = test_ml_dependencies()
    
    if local_success:
        print("\n2. Testing AWS Lambda runtime:")
        try:
            # Create executor with ML runtime
            executor = FunctionExecutor(
                config_file='config_aws_ml.yaml',
                log_level="INFO",
                runtime_memory=2048,
                runtime='ml_aws_lambda_arm_greencomp_v1'
            )
            
            # Submit the test function
            future = executor.call_async(test_ml_dependencies)
            result = future.get_result()
            
            if result:
                print("✓ ML runtime dependencies verified successfully!")
            else:
                print("✗ ML runtime dependencies test failed")
                
            executor.shutdown()
            
        except Exception as e:
            print(f"✗ Runtime test failed: {e}")
    else:
        print("✗ Local dependencies test failed, skipping runtime test")

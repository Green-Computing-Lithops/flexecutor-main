#!/usr/bin/env python3
"""
Simple test to diagnose disk space issues in Lambda functions
"""
import sys
import os

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lithops_fork')))

from lithops import FunctionExecutor

def test_disk_space_function(data):
    """Simple function to test disk space in Lambda"""
    import logging
    import os
    import shutil
    import subprocess
    
    logging.info("=== DISK SPACE TEST START ===")
    
    # Check initial disk space
    try:
        tmp_usage = shutil.disk_usage('/tmp')
        tmp_free_mb = tmp_usage.free / (1024 * 1024)
        tmp_used_mb = tmp_usage.used / (1024 * 1024)
        tmp_total_mb = tmp_usage.total / (1024 * 1024)
        
        root_usage = shutil.disk_usage('/')
        root_free_mb = root_usage.free / (1024 * 1024)
        root_used_mb = root_usage.used / (1024 * 1024)
        root_total_mb = root_usage.total / (1024 * 1024)
        
        logging.info(f"INITIAL - /tmp: {tmp_used_mb:.1f}MB used, {tmp_free_mb:.1f}MB free, {tmp_total_mb:.1f}MB total")
        logging.info(f"INITIAL - root: {root_used_mb:.1f}MB used, {root_free_mb:.1f}MB free, {root_total_mb:.1f}MB total")
        
        # Try to list /tmp contents
        result = subprocess.run(['ls', '-la', '/tmp'], capture_output=True, text=True, timeout=10)
        logging.info(f"Contents of /tmp:\n{result.stdout}")
        
        # Try to check what's using disk space
        result = subprocess.run(['du', '-sh', '/tmp', '/var', '/opt'], capture_output=True, text=True, timeout=10)
        logging.info(f"Disk usage by directory:\n{result.stdout}")
        
        # Create a test file to see available space
        test_file = '/tmp/test_disk_space.txt'
        try:
            with open(test_file, 'w') as f:
                f.write("Test file for disk space check\n" * 1000)
            logging.info("Successfully created test file")
            os.remove(test_file)
            logging.info("Successfully removed test file")
        except Exception as e:
            logging.error(f"Failed to create/remove test file: {e}")
            
        return {
            'tmp_free_mb': tmp_free_mb,
            'tmp_total_mb': tmp_total_mb,
            'root_free_mb': root_free_mb,
            'root_total_mb': root_total_mb,
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error in disk space test: {e}")
        return {'error': str(e), 'success': False}

def main():
    print("Testing disk space in AWS Lambda...")
    
    # Create executor
    executor = FunctionExecutor(log_level="INFO", runtime_memory=512)
    
    # Submit a simple test
    future = executor.call_async(test_disk_space_function, "test_data")
    
    # Wait for result
    print("Waiting for result...")
    result = future.result()
    
    print("=== RESULT ===")
    print(result)
    
    executor.shutdown()

if __name__ == "__main__":
    main()

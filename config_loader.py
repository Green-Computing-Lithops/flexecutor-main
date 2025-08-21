#!/usr/bin/env python3
"""
Configuration Loader for FlexExecutor
This utility processes YAML configuration files and replaces environment variable references.
"""

import os
import yaml
import re
from pathlib import Path


def load_env_vars(env_file=".env"):
    """Load environment variables from .env file."""
    env_path = Path(env_file)
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def process_env_vars(obj):
    """
    Recursively process a dictionary/list and replace os.getenv() calls with actual values.
    
    Args:
        obj: Dictionary, list, or string to process
        
    Returns:
        Processed object with environment variables resolved
    """
    if isinstance(obj, dict):
        return {key: process_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [process_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Look for os.getenv('VAR_NAME') or os.getenv("VAR_NAME") patterns
        pattern = r"os\.getenv\(['\"]([^'\"]+)['\"]\)"
        matches = re.findall(pattern, obj)
        
        if matches:
            result = obj
            for var_name in matches:
                env_value = os.getenv(var_name, '')
                # Replace the os.getenv call with the actual value
                result = re.sub(
                    rf"os\.getenv\(['\"]?{re.escape(var_name)}['\"]?\)",
                    env_value,
                    result
                )
            return result
        return obj
    else:
        return obj


def load_config(config_file="config_aws.yaml", env_file=".env"):
    """
    Load configuration file and process environment variables.
    
    Args:
        config_file (str): Path to the YAML configuration file
        env_file (str): Path to the .env file
        
    Returns:
        dict: Processed configuration dictionary
    """
    # First load environment variables
    load_env_vars(env_file)
    
    # Load the YAML configuration
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Process environment variable references
    processed_config = process_env_vars(config)
    
    return processed_config


def save_processed_config(config, output_file="config_processed.yaml"):
    """
    Save the processed configuration to a new YAML file.
    
    Args:
        config (dict): Processed configuration dictionary
        output_file (str): Output file path
    """
    with open(output_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)


def main():
    """Main function to demonstrate configuration loading."""
    try:
        print("FlexExecutor Configuration Loader")
        print("=" * 40)
        
        # Load and process configuration
        config = load_config()
        
        print("✓ Configuration loaded and processed successfully")
        
        # Show AWS configuration (with masked credentials)
        if 'aws' in config:
            print("\nAWS Configuration:")
            aws_config = config['aws']
            for key, value in aws_config.items():
                if key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
                    if value and len(str(value)) > 12:
                        masked_value = str(value)[:8] + '...' + str(value)[-4:]
                    else:
                        masked_value = '***' if value else 'Not set'
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
        
        # Optionally save processed config
        save_processed_config(config)
        print(f"\n✓ Processed configuration saved to config_processed.yaml")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None


if __name__ == "__main__":
    main()

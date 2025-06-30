#!/home/users/iarriazu/flexecutor-main/.venv/bin/python
"""
validate_titanic_results.py

Quick validation script to check if Titanic processing results are correct.
This can be run after executing main.py to verify the outputs.
"""

import os
import sys
import pandas as pd
from minio import Minio
import yaml
from typing import List, Dict, Any

def load_config(config_path: str = "/home/users/iarriazu/flexecutor-main/config.yaml") -> Dict[str, Any]:
    """Load MinIO configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_minio_client(config: Dict[str, Any]) -> Minio:
    """Create MinIO client."""
    minio_config = config['minio']
    endpoint = minio_config['endpoint'].replace('http://', '').replace('https://', '')
    
    return Minio(
        endpoint,
        access_key=minio_config['access_key_id'],
        secret_key=minio_config['secret_access_key'],
        secure=False
    )

def validate_processing_results(config_path: str = None) -> bool:
    """Validate that the Titanic processing produced correct results."""
    
    if config_path is None:
        config_path = "/home/users/iarriazu/flexecutor-main/config.yaml"
    
    print("🔍 Validating Titanic processing results...")
    
    try:
        # Load configuration and create client
        config = load_config(config_path)
        client = create_minio_client(config)
        bucket_name = config['minio']['storage_bucket']
        
        # 1. Check if input CSV exists
        print("\n📁 Checking input files...")
        input_objects = list(client.list_objects(bucket_name, prefix="titanic/", recursive=True))
        csv_files = [obj for obj in input_objects if obj.object_name.endswith('.csv')]
        
        if not csv_files:
            print("❌ No input CSV files found in titanic/ prefix")
            return False
        
        print(f"✅ Found {len(csv_files)} input CSV file(s):")
        for csv_file in csv_files:
            print(f"   • {csv_file.object_name} ({csv_file.size:,} bytes)")
        
        # 2. Analyze the input CSV
        print("\n📊 Analyzing input data...")
        main_csv = csv_files[0].object_name  # Use the first CSV file
        
        # Download and analyze the CSV
        temp_file = "/tmp/titanic_temp.csv"
        client.fget_object(bucket_name, main_csv, temp_file)
        df = pd.read_csv(temp_file)
        os.remove(temp_file)
        
        print(f"   📈 Total records: {len(df)}")
        print(f"   📊 Features: {list(df.columns)}")
        
        # Check required features
        required_features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Survived"]
        missing_features = [f for f in required_features if f not in df.columns]
        
        if missing_features:
            print(f"   ❌ Missing required features: {missing_features}")
            return False
        else:
            print("   ✅ All required features present")
        
        # Show data quality
        complete_records = df.dropna(subset=required_features)
        print(f"   📋 Complete records (no missing values): {len(complete_records)}")
        print(f"   📉 Records with missing values: {len(df) - len(complete_records)}")
        
        # 3. Check output files
        print("\n📤 Checking output files...")
        output_objects = list(client.list_objects(bucket_name, prefix="titanic-accuracy", recursive=True))
        accuracy_files = [obj for obj in output_objects if obj.object_name.endswith('.txt')]
        
        if not accuracy_files:
            print("❌ No accuracy output files found")
            return False
        
        print(f"✅ Found {len(accuracy_files)} accuracy file(s):")
        
        # 4. Validate accuracy values
        valid_accuracies = []
        invalid_accuracies = []
        
        for acc_file in accuracy_files:
            print(f"   📋 Checking: {acc_file.object_name}")
            try:
                # Read accuracy value
                response = client.get_object(bucket_name, acc_file.object_name)
                accuracy_content = response.read().decode('utf-8').strip()
                accuracy_value = float(accuracy_content)
                
                # Validate accuracy range
                if 0 <= accuracy_value <= 1:
                    valid_accuracies.append(accuracy_value)
                    print(f"      ✅ Valid accuracy: {accuracy_value:.4f}")
                else:
                    invalid_accuracies.append((acc_file.object_name, accuracy_value, "Out of range"))
                    print(f"      ❌ Invalid accuracy: {accuracy_value} (out of range [0,1])")
                    
            except Exception as e:
                invalid_accuracies.append((acc_file.object_name, None, str(e)))
                print(f"      ❌ Error reading file: {e}")
        
        # 5. Summary and validation
        print("\n📋 VALIDATION SUMMARY")
        print("=" * 50)
        
        success = True
        
        print(f"Input CSV files: {len(csv_files)} ✅")
        print(f"Required features: {'✅ Present' if not missing_features else '❌ Missing: ' + str(missing_features)}")
        print(f"Output accuracy files: {len(accuracy_files)} {'✅' if accuracy_files else '❌'}")
        print(f"Valid accuracy values: {len(valid_accuracies)} {'✅' if valid_accuracies else '❌'}")
        print(f"Invalid accuracy values: {len(invalid_accuracies)} {'✅' if not invalid_accuracies else '❌'}")
        
        if valid_accuracies:
            avg_accuracy = sum(valid_accuracies) / len(valid_accuracies)
            min_accuracy = min(valid_accuracies)
            max_accuracy = max(valid_accuracies)
            
            print(f"\n📊 ACCURACY STATISTICS:")
            print(f"   Average: {avg_accuracy:.4f}")
            print(f"   Range: {min_accuracy:.4f} - {max_accuracy:.4f}")
            print(f"   Count: {len(valid_accuracies)}")
            
            # Basic sanity checks
            if avg_accuracy < 0.5:
                print("   ⚠️  Warning: Average accuracy is quite low (<0.5)")
                print("      This might indicate issues with the data or model")
            else:
                print("   ✅ Accuracy looks reasonable")
        
        if invalid_accuracies:
            print(f"\n❌ INVALID RESULTS:")
            for filename, value, reason in invalid_accuracies:
                print(f"   • {filename}: {reason}")
            success = False
        
        if missing_features:
            success = False
        
        if not accuracy_files:
            success = False
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 VALIDATION PASSED: All results look correct!")
        else:
            print("❌ VALIDATION FAILED: Issues detected in the results")
            
        return success
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Titanic processing results")
    parser.add_argument("--config", "-c", help="Path to config.yaml file")
    
    args = parser.parse_args()
    
    try:
        success = validate_processing_results(args.config)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Validation interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/home/users/iarriazu/flexecutor-main/.venv/bin/python
"""
monitor_minio_processing.py

Monitor CSV processing in MinIO for the Titanic workflow.
This script helps you:
1. Check which CSV files are being processed
2. Monitor intermediate chunks created during processing
3. Validate output accuracy files
4. Provide debugging information
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from minio import Minio
from minio.error import S3Error
import yaml

class TitanicMinIOMonitor:
    def __init__(self, config_path: str = None):
        """Initialize the monitor with MinIO configuration."""
        if config_path is None:
            config_path = "/home/users/iarriazu/flexecutor-main/config.yaml"
        
        self.config = self._load_config(config_path)
        self.client = self._create_minio_client()
        self.bucket_name = self.config['minio']['storage_bucket']
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            sys.exit(1)
    
    def _create_minio_client(self) -> Minio:
        """Create MinIO client from configuration."""
        minio_config = self.config['minio']
        endpoint = minio_config['endpoint'].replace('http://', '').replace('https://', '')
        
        return Minio(
            endpoint,
            access_key=minio_config['access_key_id'],
            secret_key=minio_config['secret_access_key'],
            secure=False  # Set to True if using HTTPS
        )
    
    def list_input_csv_files(self) -> List[Dict[str, Any]]:
        """List all CSV files in the titanic input directory."""
        print("🔍 Checking input CSV files...")
        input_files = []
        
        try:
            objects = self.client.list_objects(self.bucket_name, prefix="titanic/", recursive=True)
            for obj in objects:
                if obj.object_name.endswith('.csv'):
                    # Get file stats
                    stat = self.client.stat_object(self.bucket_name, obj.object_name)
                    input_files.append({
                        'name': obj.object_name,
                        'size': stat.size,
                        'last_modified': stat.last_modified,
                        'etag': stat.etag
                    })
                    
        except S3Error as e:
            print(f"❌ Error accessing MinIO: {e}")
            return []
        
        if input_files:
            print(f"📁 Found {len(input_files)} input CSV file(s):")
            for file_info in input_files:
                print(f"  • {file_info['name']}")
                print(f"    Size: {file_info['size']:,} bytes")
                print(f"    Last modified: {file_info['last_modified']}")
                print()
        else:
            print("⚠️  No CSV files found in titanic/ prefix")
            
        return input_files
    
    def check_csv_content(self, csv_path: str) -> Dict[str, Any]:
        """Analyze the content of a CSV file."""
        print(f"📊 Analyzing CSV content: {csv_path}")
        
        try:
            # Download the CSV file temporarily
            temp_file = f"/tmp/{os.path.basename(csv_path)}"
            self.client.fget_object(self.bucket_name, csv_path, temp_file)
            
            # Analyze with pandas
            df = pd.read_csv(temp_file)
            
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.to_dict(),
                'sample_data': df.head().to_dict('records')
            }
            
            # Check for required features
            required_features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Survived"]
            missing_features = [f for f in required_features if f not in df.columns]
            analysis['missing_required_features'] = missing_features
            
            # Clean up temp file
            os.remove(temp_file)
            
            # Print analysis
            print(f"  📈 Total rows: {analysis['total_rows']}")
            print(f"  📊 Total columns: {analysis['total_columns']}")
            print(f"  🏷️  Columns: {', '.join(analysis['columns'])}")
            
            if missing_features:
                print(f"  ⚠️  Missing required features: {', '.join(missing_features)}")
            else:
                print("  ✅ All required features present")
                
            # Show missing values for key features
            key_missing = {k: v for k, v in analysis['missing_values'].items() 
                          if k in required_features and v > 0}
            if key_missing:
                print("  🔍 Missing values in key features:")
                for feature, count in key_missing.items():
                    print(f"    • {feature}: {count} missing ({count/analysis['total_rows']*100:.1f}%)")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing CSV {csv_path}: {e}")
            return {}
    
    def list_processing_artifacts(self) -> Dict[str, List[str]]:
        """List all processing artifacts (chunks, outputs, etc.)."""
        print("🔍 Checking processing artifacts...")
        
        artifacts = {
            'chunks': [],
            'outputs': [],
            'temporary': []
        }
        
        try:
            # Check for various prefixes that might be created during processing
            prefixes_to_check = [
                'titanic-chunk-',
                'titanic-accuracy',
                'lithops-',
                'tmp-',
                'temp-'
            ]
            
            for prefix in prefixes_to_check:
                objects = list(self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True))
                for obj in objects:
                    if 'chunk' in prefix.lower():
                        artifacts['chunks'].append(obj.object_name)
                    elif 'accuracy' in prefix.lower():
                        artifacts['outputs'].append(obj.object_name)
                    elif any(x in prefix.lower() for x in ['lithops', 'tmp', 'temp']):
                        artifacts['temporary'].append(obj.object_name)
            
            # Also check for any objects that might be Lithops-related
            all_objects = list(self.client.list_objects(self.bucket_name, recursive=True))
            for obj in all_objects:
                obj_name = obj.object_name.lower()
                if any(x in obj_name for x in ['lithops', 'executor', 'stage']):
                    if obj.object_name not in artifacts['temporary']:
                        artifacts['temporary'].append(obj.object_name)
                        
        except S3Error as e:
            print(f"❌ Error listing artifacts: {e}")
        
        # Print results
        total_artifacts = sum(len(v) for v in artifacts.values())
        if total_artifacts > 0:
            print(f"📦 Found {total_artifacts} processing artifacts:")
            
            if artifacts['chunks']:
                print(f"  🧩 Chunks ({len(artifacts['chunks'])}):")
                for chunk in sorted(artifacts['chunks'])[:10]:  # Show first 10
                    print(f"    • {chunk}")
                if len(artifacts['chunks']) > 10:
                    print(f"    ... and {len(artifacts['chunks']) - 10} more")
                    
            if artifacts['outputs']:
                print(f"  📤 Outputs ({len(artifacts['outputs'])}):")
                for output in sorted(artifacts['outputs']):
                    print(f"    • {output}")
                    
            if artifacts['temporary']:
                print(f"  🗂️  Temporary files ({len(artifacts['temporary'])}):")
                for temp in sorted(artifacts['temporary'])[:5]:  # Show first 5
                    print(f"    • {temp}")
                if len(artifacts['temporary']) > 5:
                    print(f"    ... and {len(artifacts['temporary']) - 5} more")
        else:
            print("📦 No processing artifacts found")
            
        return artifacts
    
    def validate_outputs(self) -> Dict[str, Any]:
        """Validate the accuracy output files."""
        print("✅ Validating output files...")
        
        validation_results = {
            'accuracy_files': [],
            'valid_accuracies': [],
            'invalid_accuracies': [],
            'average_accuracy': None,
            'total_outputs': 0
        }
        
        try:
            # Look for accuracy output files
            objects = list(self.client.list_objects(self.bucket_name, prefix="titanic-accuracy", recursive=True))
            
            for obj in objects:
                if obj.object_name.endswith('.txt'):
                    validation_results['accuracy_files'].append(obj.object_name)
                    
                    try:
                        # Download and read the accuracy file
                        response = self.client.get_object(self.bucket_name, obj.object_name)
                        accuracy_content = response.read().decode('utf-8').strip()
                        accuracy_value = float(accuracy_content)
                        
                        if 0 <= accuracy_value <= 1:
                            validation_results['valid_accuracies'].append({
                                'file': obj.object_name,
                                'accuracy': accuracy_value
                            })
                        else:
                            validation_results['invalid_accuracies'].append({
                                'file': obj.object_name,
                                'accuracy': accuracy_value,
                                'reason': 'Out of valid range [0, 1]'
                            })
                            
                    except Exception as e:
                        validation_results['invalid_accuracies'].append({
                            'file': obj.object_name,
                            'accuracy': None,
                            'reason': f'Failed to parse: {e}'
                        })
                        
            validation_results['total_outputs'] = len(validation_results['accuracy_files'])
            
            # Calculate average accuracy
            if validation_results['valid_accuracies']:
                valid_acc_values = [item['accuracy'] for item in validation_results['valid_accuracies']]
                validation_results['average_accuracy'] = sum(valid_acc_values) / len(valid_acc_values)
            
            # Print results
            if validation_results['total_outputs'] > 0:
                print(f"📊 Found {validation_results['total_outputs']} output file(s)")
                print(f"✅ Valid accuracies: {len(validation_results['valid_accuracies'])}")
                print(f"❌ Invalid accuracies: {len(validation_results['invalid_accuracies'])}")
                
                if validation_results['valid_accuracies']:
                    print(f"📈 Average accuracy: {validation_results['average_accuracy']:.4f}")
                    print("📋 Individual accuracies:")
                    for item in validation_results['valid_accuracies']:
                        print(f"  • {item['file']}: {item['accuracy']:.4f}")
                        
                if validation_results['invalid_accuracies']:
                    print("⚠️  Invalid accuracy files:")
                    for item in validation_results['invalid_accuracies']:
                        print(f"  • {item['file']}: {item['reason']}")
                        
            else:
                print("⚠️  No output files found")
                
        except S3Error as e:
            print(f"❌ Error validating outputs: {e}")
            
        return validation_results
    
    def cleanup_processing_artifacts(self, confirm: bool = False):
        """Clean up temporary processing artifacts."""
        print("🧹 Cleanup processing artifacts...")
        
        if not confirm:
            response = input("This will delete temporary processing files. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Cleanup cancelled.")
                return
        
        prefixes_to_clean = [
            'lithops-',
            'tmp-',
            'temp-',
            'titanic-chunk-'  # Be careful with this one
        ]
        
        for prefix in prefixes_to_clean:
            try:
                objects = list(self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True))
                if objects:
                    print(f"🗑️  Deleting {len(objects)} objects with prefix '{prefix}'...")
                    for obj in objects:
                        self.client.remove_object(self.bucket_name, obj.object_name)
                        print(f"  ✅ Deleted: {obj.object_name}")
                else:
                    print(f"  ℹ️  No objects found with prefix '{prefix}'")
            except S3Error as e:
                print(f"❌ Error cleaning prefix '{prefix}': {e}")
    
    def full_monitoring_report(self):
        """Generate a complete monitoring report."""
        print("=" * 80)
        print("🚢 TITANIC MINIO PROCESSING MONITOR")
        print("=" * 80)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🪣 Bucket: {self.bucket_name}")
        print(f"🔗 Endpoint: {self.config['minio']['endpoint']}")
        print()
        
        # 1. Check input files
        input_files = self.list_input_csv_files()
        print()
        
        # 2. Analyze CSV content if files exist
        if input_files:
            for file_info in input_files:
                self.check_csv_content(file_info['name'])
                print()
        
        # 3. Check processing artifacts
        artifacts = self.list_processing_artifacts()
        print()
        
        # 4. Validate outputs
        validation = self.validate_outputs()
        print()
        
        # 5. Summary
        print("=" * 80)
        print("📋 SUMMARY")
        print("=" * 80)
        print(f"• Input CSV files: {len(input_files)}")
        print(f"• Processing chunks: {len(artifacts.get('chunks', []))}")
        print(f"• Output files: {len(artifacts.get('outputs', []))}")
        print(f"• Temporary files: {len(artifacts.get('temporary', []))}")
        print(f"• Valid accuracy results: {len(validation.get('valid_accuracies', []))}")
        
        if validation.get('average_accuracy') is not None:
            print(f"• Average accuracy: {validation['average_accuracy']:.4f}")
            
        print("=" * 80)


def main():
    """Main function to run the monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Titanic CSV processing in MinIO")
    parser.add_argument("--config", "-c", help="Path to config.yaml file")
    parser.add_argument("--cleanup", action="store_true", help="Clean up temporary files")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch for changes (not implemented)")
    
    args = parser.parse_args()
    
    try:
        monitor = TitanicMinIOMonitor(args.config)
        
        if args.cleanup:
            monitor.cleanup_processing_artifacts()
        else:
            monitor.full_monitoring_report()
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

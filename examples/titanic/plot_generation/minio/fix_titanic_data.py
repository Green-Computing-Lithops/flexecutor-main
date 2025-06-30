#!/home/users/iarriazu/flexecutor-main/.venv/bin/python
"""
fix_titanic_data.py

Fix the Titanic data setup by:
1. Cleaning up old chunk files in MinIO  
2. Uploading the correct full titanic.csv file
3. Ensuring proper single-file input for dynamic chunking
"""

import os
import sys
import yaml
from minio import Minio
from minio.error import S3Error

def load_config(config_path: str = "config.yaml") -> dict:
    """Load MinIO configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_minio_client(config: dict) -> Minio:
    """Create MinIO client."""
    minio_config = config['minio']
    endpoint = minio_config['endpoint'].replace('http://', '').replace('https://', '')
    
    return Minio(
        endpoint,
        access_key=minio_config['access_key_id'],
        secret_key=minio_config['secret_access_key'],
        secure=False
    )

def cleanup_old_files(client: Minio, bucket_name: str):
    """Remove old chunk files and incorrect titanic.csv from MinIO."""
    print("🧹 Cleaning up old files in MinIO...")
    
    # Files to remove
    files_to_remove = []
    
    # List all files in titanic/ prefix
    try:
        objects = list(client.list_objects(bucket_name, prefix="titanic/", recursive=True))
        for obj in objects:
            if obj.object_name.startswith("titanic/chunk_") or obj.object_name == "titanic/titanic.csv":
                files_to_remove.append(obj.object_name)
                
        if files_to_remove:
            print(f"📋 Found {len(files_to_remove)} files to remove:")
            for filename in files_to_remove:
                print(f"  • {filename}")
            
            # Ask for confirmation
            response = input("Remove these files? (y/N): ")
            if response.lower() == 'y':
                for filename in files_to_remove:
                    try:
                        client.remove_object(bucket_name, filename)
                        print(f"  ✅ Removed: {filename}")
                    except S3Error as e:
                        print(f"  ❌ Error removing {filename}: {e}")
            else:
                print("Cleanup cancelled.")
                return False
        else:
            print("  ℹ️  No old files found to remove")
            
    except S3Error as e:
        print(f"❌ Error listing files: {e}")
        return False
        
    return True

def upload_correct_file(client: Minio, bucket_name: str, local_file_path: str):
    """Upload the correct full titanic.csv file."""
    print("📤 Uploading correct titanic.csv file...")
    
    if not os.path.exists(local_file_path):
        print(f"❌ Local file not found: {local_file_path}")
        return False
        
    # Check file size
    file_size = os.path.getsize(local_file_path)
    print(f"  📁 Local file size: {file_size:,} bytes")
    
    # Count rows
    with open(local_file_path, 'r') as f:
        row_count = sum(1 for line in f) - 1  # Subtract header
    print(f"  📊 Local file rows: {row_count:,}")
    
    if row_count < 800:  # Should be around 891 rows
        print(f"⚠️  Warning: File seems small ({row_count} rows). Expected ~891 rows.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    try:
        # Upload the file
        client.fput_object(bucket_name, "titanic/titanic.csv", local_file_path)
        print("  ✅ File uploaded successfully!")
        
        # Verify upload
        stat = client.stat_object(bucket_name, "titanic/titanic.csv")
        print(f"  📋 Uploaded file size: {stat.size:,} bytes")
        
        return True
        
    except S3Error as e:
        print(f"❌ Error uploading file: {e}")
        return False

def verify_setup(client: Minio, bucket_name: str):
    """Verify the final setup is correct."""
    print("✅ Verifying final setup...")
    
    try:
        # List files in titanic/ prefix
        objects = list(client.list_objects(bucket_name, prefix="titanic/", recursive=True))
        csv_files = [obj for obj in objects if obj.object_name.endswith('.csv')]
        
        print(f"  📁 Files in titanic/ prefix: {len(csv_files)}")
        
        if len(csv_files) == 1 and csv_files[0].object_name == "titanic/titanic.csv":
            print("  ✅ Perfect! Only titanic.csv exists (as it should)")
            
            # Check file size
            stat = client.stat_object(bucket_name, "titanic/titanic.csv")
            print(f"  📊 File size: {stat.size:,} bytes")
            
            if stat.size > 50000:  # Should be around 60KB
                print("  ✅ File size looks correct for full dataset")
            else:
                print("  ⚠️  File size seems small - might not be full dataset")
                
        else:
            print("  ❌ Wrong file setup:")
            for csv_file in csv_files:
                print(f"    • {csv_file.object_name}")
            return False
            
    except S3Error as e:
        print(f"❌ Error verifying setup: {e}")
        return False
        
    return True

def main():
    """Main function."""
    print("=" * 80)
    print("🔧 TITANIC DATA SETUP FIX")
    print("=" * 80)
    print("This script will:")
    print("1. Remove old chunk files and incorrect titanic.csv from MinIO")
    print("2. Upload the correct full titanic.csv file")
    print("3. Verify the setup for proper dynamic chunking")
    print()
    
    # Configuration
    config_path = "config.yaml"
    local_file_path = "test-bucket/titanic/titanic.csv"
    
    try:
        # Load config and create client
        config = load_config(config_path)
        client = create_minio_client(config)
        bucket_name = config['minio']['storage_bucket']
        
        print(f"📋 Bucket: {bucket_name}")
        print(f"🔗 Endpoint: {config['minio']['endpoint']}")
        print(f"📁 Local file: {local_file_path}")
        print()
        
        # Step 1: Cleanup
        if not cleanup_old_files(client, bucket_name):
            print("❌ Cleanup failed")
            return False
        print()
        
        # Step 2: Upload correct file
        if not upload_correct_file(client, bucket_name, local_file_path):
            print("❌ Upload failed")
            return False
        print()
        
        # Step 3: Verify
        if not verify_setup(client, bucket_name):
            print("❌ Verification failed")
            return False
        print()
        
        # Success message
        print("=" * 80)
        print("🎉 SUCCESS!")
        print("=" * 80)
        print("Your Titanic data is now properly set up:")
        print("• Single titanic.csv file in MinIO")
        print("• Full dataset ready for dynamic chunking")
        print("• No interfering chunk files")
        print()
        print("Now you can run your main.py and it will:")
        print("• Take the single titanic.csv file")
        print("• Automatically split it into chunks for workers")
        print("• Process each chunk independently")
        print("• Generate one accuracy result per chunk")
        print()
        print("Next steps:")
        print("  python examples/titanic/main.py")
        print("  python examples/titanic/validate_titanic_results.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

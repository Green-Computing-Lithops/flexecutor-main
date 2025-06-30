#!/home/users/iarriazu/flexecutor-main/.venv/bin/python
"""
Clean up old MinIO artifacts from previous runs.
"""

import yaml
from minio import Minio
from minio.error import S3Error

def cleanup_old_files():
    # Load config
    with open("/home/users/iarriazu/flexecutor-main/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Create client
    minio_config = config['minio']
    endpoint = minio_config['endpoint'].replace('http://', '').replace('https://', '')
    
    client = Minio(
        endpoint,
        access_key=minio_config['access_key_id'],
        secret_key=minio_config['secret_access_key'],
        secure=False
    )
    bucket_name = minio_config['storage_bucket']
    
    # Prefixes to clean
    prefixes_to_clean = [
        'titanic-accuracy',
        'lithops.jobs',
        'titanic/chunk_'
    ]
    
    print("🧹 Cleaning up old artifacts...")
    
    for prefix in prefixes_to_clean:
        try:
            objects = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))
            if objects:
                print(f"  🗑️  Deleting {len(objects)} objects with prefix '{prefix}'")
                for obj in objects:
                    client.remove_object(bucket_name, obj.object_name)
                    print(f"    ✅ Deleted: {obj.object_name}")
            else:
                print(f"  ℹ️  No objects found with prefix '{prefix}'")
        except S3Error as e:
            print(f"  ❌ Error cleaning prefix '{prefix}': {e}")
    
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    cleanup_old_files()

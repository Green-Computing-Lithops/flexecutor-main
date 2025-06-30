#!/usr/bin/env python3
"""
upload_titanic_to_minio.py

Upload the expanded Titanic dataset to MinIO, replacing the existing one.
"""

import os
import sys
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject

# MinIO Configuration (based on the run_titanic_workflow script)
MINIO_ENDPOINT = "192.168.5.24:9000"
MINIO_ACCESS_KEY = "lab144"
MINIO_SECRET_KEY = "astl1a4b4"
MINIO_BUCKET = "test-bucket"

# File paths
LOCAL_TITANIC_FILE = "/home/users/iarriazu/flexecutor-main/test-bucket/titanic/titanic.csv"
MINIO_TITANIC_PATH = "titanic/titanic.csv"

def get_file_size_mb(file_path):
    """Get file size in MB."""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024), size_bytes

def list_titanic_objects(client):
    """List all objects under the titanic prefix."""
    try:
        objects = list(client.list_objects(MINIO_BUCKET, prefix="titanic/", recursive=True))
        return objects
    except Exception as e:
        print(f"[✗] Error listing titanic objects: {e}")
        return []

def cleanup_existing_titanic_data(client):
    """Remove existing titanic data from MinIO."""
    print(f"[+] Checking for existing titanic data in MinIO...")
    
    objects = list_titanic_objects(client)
    
    if not objects:
        print(f"[+] No existing titanic data found in MinIO")
        return True
    
    print(f"[+] Found {len(objects)} existing titanic object(s):")
    total_size = 0
    for obj in objects:
        size_mb = obj.size / (1024 * 1024)
        total_size += obj.size
        print(f"    - {obj.object_name}: {size_mb:.2f} MB")
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"[+] Total existing data size: {total_size_mb:.2f} MB")
    
    # Delete existing objects
    to_delete = [DeleteObject(obj.object_name) for obj in objects]
    print(f"[+] Deleting {len(to_delete)} existing titanic objects...")
    
    try:
        errors = client.remove_objects(MINIO_BUCKET, to_delete)
        error_count = 0
        for err in errors:
            print(f"    ✗ Failed to delete {err.object_name}: {err}")
            error_count += 1
        
        if error_count == 0:
            print(f"[✓] Successfully deleted all existing titanic data")
            return True
        else:
            print(f"[✗] Failed to delete {error_count} objects")
            return False
            
    except Exception as e:
        print(f"[✗] Error during cleanup: {e}")
        return False

def upload_titanic_data(client):
    """Upload the expanded titanic dataset to MinIO."""
    print(f"[+] Uploading expanded titanic dataset...")
    
    # Check local file
    if not os.path.exists(LOCAL_TITANIC_FILE):
        print(f"[✗] Local file not found: {LOCAL_TITANIC_FILE}")
        return False
    
    size_mb, size_bytes = get_file_size_mb(LOCAL_TITANIC_FILE)
    print(f"[+] Local file size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
    
    try:
        # Upload the file
        print(f"[+] Uploading to {MINIO_BUCKET}/{MINIO_TITANIC_PATH}...")
        
        client.fput_object(
            bucket_name=MINIO_BUCKET,
            object_name=MINIO_TITANIC_PATH,
            file_path=LOCAL_TITANIC_FILE,
            content_type="text/csv"
        )
        
        print(f"[✓] Successfully uploaded titanic dataset to MinIO")
        return True
        
    except Exception as e:
        print(f"[✗] Error uploading file: {e}")
        return False

def verify_upload(client):
    """Verify the uploaded file."""
    print(f"[+] Verifying uploaded file...")
    
    try:
        # Get object info
        obj_info = client.stat_object(MINIO_BUCKET, MINIO_TITANIC_PATH)
        
        size_mb = obj_info.size / (1024 * 1024)
        print(f"[✓] File successfully uploaded:")
        print(f"    - Object: {MINIO_TITANIC_PATH}")
        print(f"    - Size: {size_mb:.2f} MB ({obj_info.size:,} bytes)")
        print(f"    - ETag: {obj_info.etag}")
        print(f"    - Last Modified: {obj_info.last_modified}")
        
        return True
        
    except Exception as e:
        print(f"[✗] Error verifying upload: {e}")
        return False

def main():
    print("="*70)
    print("UPLOAD EXPANDED TITANIC DATASET TO MINIO")
    print("="*70)
    
    # Check local file first
    if not os.path.exists(LOCAL_TITANIC_FILE):
        print(f"[✗] Local Titanic file not found: {LOCAL_TITANIC_FILE}")
        sys.exit(1)
    
    local_size_mb, local_size_bytes = get_file_size_mb(LOCAL_TITANIC_FILE)
    print(f"[+] Local file: {LOCAL_TITANIC_FILE}")
    print(f"[+] Local file size: {local_size_mb:.2f} MB ({local_size_bytes:,} bytes)")
    
    # Initialize MinIO client
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        print(f"[✓] Connected to MinIO at {MINIO_ENDPOINT}")
        
    except Exception as e:
        print(f"[✗] Failed to connect to MinIO: {e}")
        sys.exit(1)
    
    # Check if bucket exists
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"[✗] Bucket '{MINIO_BUCKET}' does not exist")
            sys.exit(1)
        print(f"[✓] Bucket '{MINIO_BUCKET}' exists")
        
    except Exception as e:
        print(f"[✗] Error checking bucket: {e}")
        sys.exit(1)
    
    # Step 1: Clean up existing titanic data
    if not cleanup_existing_titanic_data(client):
        print(f"[✗] Failed to cleanup existing data")
        sys.exit(1)
    
    # Step 2: Upload new data
    if not upload_titanic_data(client):
        print(f"[✗] Failed to upload new data")
        sys.exit(1)
    
    # Step 3: Verify upload
    if not verify_upload(client):
        print(f"[✗] Failed to verify upload")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("UPLOAD COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"[✓] Expanded Titanic dataset ({local_size_mb:.2f} MB) uploaded to MinIO")
    print(f"[✓] Ready to run workflow with {local_size_bytes:,} bytes of data")
    print(f"[✓] Location: {MINIO_BUCKET}/{MINIO_TITANIC_PATH}")

if __name__ == "__main__":
    main()

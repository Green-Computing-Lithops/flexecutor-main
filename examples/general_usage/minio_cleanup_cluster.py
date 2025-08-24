#!/usr/bin/env python3
"""
minio_cleanup_cluster.py

Delete all objects under specified "temporary" prefixes in a MinIO bucket.
Configured for use with the cluster's Minio storage.
"""

from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject

# ───────────────────────────────────────────────────────────────────────────────
# CLUSTER MINIO CONFIGURATION
MINIO_ENDPOINT    = "storage4-10Gbit:9000"  # Without http:// prefix
MINIO_ACCESS_KEY  = "lab144"
MINIO_SECRET_KEY  = "astl1a4b4"
MINIO_BUCKET      = "test-bucket"
# ───────────────────────────────────────────────────────────────────────────────

def cleanup_temp_prefixes(
    client: Minio,
    bucket_name: str,
    prefixes: list[str],
) -> None:
    """
    For each prefix in `prefixes`, list all objects under that prefix
    (recursively) and delete them using DeleteObject.
    """
    for prefix in prefixes:
        # List all objects under this prefix
        objects = list(client.list_objects(bucket_name, prefix=prefix, recursive=True))
        if not objects:
            print(f"[+] No objects found under prefix: {prefix!r}")
            continue

        # Wrap each object_name in a DeleteObject
        to_delete = [DeleteObject(obj.object_name) for obj in objects]
        print(f"[+] Deleting {len(to_delete)} objects under prefix: {prefix!r} …")

        # Bulk-delete
        errors = client.remove_objects(bucket_name, to_delete)
        for err in errors:
            print(f"    ✗ Failed to delete {err.object_name}: {err}")
        print(f"[✓] Done with prefix: {prefix!r}\n")


def main():
    # Connect to the cluster's Minio storage
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,  # Using http:// not https://
    )

    # List of prefixes to clean up
    temp_prefixes = [
        "training-data-transform",
        "vectors-pca",
        "models",
        "predictions",
        "accuracies",
        "forests",
        "lithops.jobs",
        "lithops.runtimes"
    ]

    try:
        # Check if bucket exists
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"ERROR: Bucket '{MINIO_BUCKET}' does not exist")
            return
            
        print(f"[+] Connected to Minio at {MINIO_ENDPOINT}")
        print(f"[+] Starting cleanup of bucket: {MINIO_BUCKET}")
        cleanup_temp_prefixes(client, MINIO_BUCKET, temp_prefixes)
        print("[✓] Cleanup completed successfully")
    except S3Error as err:
        print("ERROR communicating with MinIO:", err)


if __name__ == "__main__":
    main()

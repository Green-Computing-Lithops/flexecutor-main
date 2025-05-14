#!/usr/bin/env python3
"""
minio_cleanup.py

Delete all objects under specified “temporary” prefixes in a MinIO bucket.
"""

from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject  # <-- use DeleteObject here

# ───────────────────────────────────────────────────────────────────────────────
# YOUR MINIO CONFIGURATION (hard-coded)
MINIO_ENDPOINT    = "192.168.1.168:9000"
MINIO_ACCESS_KEY  = "minioadmin"
MINIO_SECRET_KEY  = "minioadmin"
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
    # Use the hard-coded constants above
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,  # change to True if using HTTPS
    )

    temp_prefixes = [
        "training-data-transform",
        "vectors-pca",
        "models",
        "predictions",
        "accuracies",
        "forests",
    ]

    try:
        cleanup_temp_prefixes(client, MINIO_BUCKET, temp_prefixes)
    except S3Error as err:
        print("ERROR communicating with MinIO:", err)


if __name__ == "__main__":
    main()

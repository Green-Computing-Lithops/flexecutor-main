#!/usr/bin/env python3
"""
Verification script to check if Titanic workflow results are correct
"""

from minio import Minio
import statistics

# MinIO configuration
MINIO_ENDPOINT = "192.168.5.24:9000"
MINIO_ACCESS_KEY = "lab144"
MINIO_SECRET_KEY = "astl1a4b4"
MINIO_BUCKET = "test-bucket"

def verify_titanic_results():
    """Verify the Titanic workflow results."""
    try:
        client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
        
        print("=== TITANIC WORKFLOW VERIFICATION ===")
        
        # Check input data
        input_objects = list(client.list_objects(MINIO_BUCKET, prefix='titanic/', recursive=True))
        print(f"✓ Input files: {len(input_objects)}")
        
        # Check results
        accuracy_objects = list(client.list_objects(MINIO_BUCKET, prefix='titanic-accuracy', recursive=True))
        print(f"✓ Result files: {len(accuracy_objects)}")
        
        if not accuracy_objects:
            print("❌ NO RESULTS FOUND - Workflow failed or incomplete")
            return False
        
        # Read and validate accuracy scores
        accuracies = []
        print("\n=== ACCURACY SCORES ===")
        for obj in accuracy_objects:
            try:
                response = client.get_object(MINIO_BUCKET, obj.object_name)
                accuracy = float(response.read().decode('utf-8').strip())
                accuracies.append(accuracy)
                print(f"  {obj.object_name}: {accuracy:.4f}")
                response.close()
            except Exception as e:
                print(f"  ❌ {obj.object_name}: Error reading - {e}")
        
        # Statistical analysis
        if accuracies:
            avg_accuracy = statistics.mean(accuracies)
            min_accuracy = min(accuracies)
            max_accuracy = max(accuracies)
            
            print(f"\n=== STATISTICS ===")
            print(f"  Average accuracy: {avg_accuracy:.4f}")
            print(f"  Min accuracy: {min_accuracy:.4f}")
            print(f"  Max accuracy: {max_accuracy:.4f}")
            print(f"  Number of chunks: {len(accuracies)}")
            
            # Validation
            if 0.5 <= avg_accuracy <= 0.9:
                print(f"✅ RESULTS VALID - Average accuracy {avg_accuracy:.4f} is reasonable")
                return True
            else:
                print(f"❌ RESULTS SUSPICIOUS - Average accuracy {avg_accuracy:.4f} is unusual")
                return False
        else:
            print("❌ NO VALID ACCURACY SCORES FOUND")
            return False
            
    except Exception as e:
        print(f"❌ VERIFICATION FAILED: {e}")
        return False

if __name__ == "__main__":
    verify_titanic_results()

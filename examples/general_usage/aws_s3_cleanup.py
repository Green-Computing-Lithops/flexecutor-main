"""
AWS S3 Cleanup Utility

This module provides comprehensive S3 cleanup functionality for FlexExecutor workflows.
It provides a global cleanup function that deletes all temporary files and directories
for any workflow type.

Author: FlexExecutor Team
Date: August 2025
"""

import os
import subprocess
from typing import List, Optional, Tuple


class S3Cleaner:
    """
    A comprehensive S3 cleanup utility for FlexExecutor workflows.
    
    This class provides a global cleanup method that removes all temporary files
    and directories generated during workflow execution, helping to manage storage
    costs and maintain clean S3 buckets.
    """
    
    # Comprehensive list of all temporary directories used across all workflows
    ALL_TEMP_DIRECTORIES = [
        # Core Lithops directories
        "lithops.jobs/",
        "lithops.runtimes/",
        "lithops.temp/",
        
        # ML workflow directories
        "vectors-pca/",
        "training-data-transform/",
        "pi_estimation_result/",
        "models/",
        "forests/",
        "predictions/",
        "accuracies/",
        "ml-temp/",
        "model-cache/",
        "training-cache/",
        "features/",
        "datasets/",
        
        # Video workflow directories
        "classification/",
        "filtered-frames/", 
        "video-chunks/",
        "mainframes/",
        "frames/",
        "segments/",
        "thumbnails/",
        "video-temp/",
        "moviepy-temp/",
        "ffmpeg-temp/",
        
        # General temporary directories
        "temp/",
        "tmp/",
        "cache/",
        "intermediate/",
        "workflow-temp/",
        "processing/",
        
        # Legacy and specialized directories
        "titanic-accuracy/",
        "montecarlo-temp/",
        "radio-temp/",
        
        # Pattern-based directories (will be handled separately)
        "video_split_*/",
        "temp_audio*/",
        "moviepy_*/",
        "ffmpeg_*/",
    ]
    
    # File patterns to clean up
    TEMP_FILE_PATTERNS = [
        "*.tmp",
        "*.temp",
        "*.m4a",
        "*temp*",
        "*moviepy*",
        "*ffmpeg*",
        "*.cache",
        "*.log",
        "*-temp-*",
        "*_temp_*",
    ]
    
    def __init__(self, bucket_name: str = "lithops-us-east-1-45dk", timeout: int = 300):
        """
        Initialize the S3 cleaner.
        
        Args:
            bucket_name: The S3 bucket name to clean
            timeout: Timeout in seconds for each cleanup operation
        """
        self.bucket_name = bucket_name
        self.timeout = timeout
        self.env = os.environ.copy()  # Inherit AWS credentials from environment
    
    def test_s3_access(self) -> bool:
        """
        Test if we have proper S3 access with current credentials.
        
        Returns:
            bool: True if S3 access is working, False otherwise
        """
        try:
            cmd = ["aws", "s3", "ls", f"s3://{self.bucket_name}/"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=self.env)
            return result.returncode == 0
        except Exception:
            return False
    
    def global_cleanup(self) -> Tuple[bool, int]:
        """
        Perform a comprehensive cleanup of all temporary files and directories.
        This is the main cleanup function that should be used for all workflows.
        
        Returns:
            Tuple[bool, int]: (success_status, total_files_deleted)
        """
        print(f"\n{'='*60}")
        print(f"GLOBAL AWS S3 CLEANUP - ALL TEMPORARY FILES")
        print(f"{'='*60}")
        
        # Test S3 access first
        if not self.test_s3_access():
            print("[✗] AWS S3 access failed. Please check your credentials.")
            return False, 0
        
        print("[✓] AWS S3 access confirmed")
        print("[+] Starting comprehensive cleanup of all temporary files...")
        
        cleanup_success = True
        total_deleted = 0
        
        # Step 1: Clean up all known temporary directories
        print(f"[+] Cleaning up {len(self.ALL_TEMP_DIRECTORIES)} known temporary directories...")
        for directory in self.ALL_TEMP_DIRECTORIES:
            try:
                print(f"[+] Removing {directory}...")
                cmd = ["aws", "s3", "rm", f"s3://{self.bucket_name}/{directory}", "--recursive"]
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=self.timeout, env=self.env)
                
                if result.returncode == 0:
                    deleted_count = result.stdout.count("delete:")
                    if deleted_count > 0:
                        print(f"[✓] Removed {deleted_count} files from {directory}")
                        total_deleted += deleted_count
                    else:
                        print(f"[i] No files found in {directory}")
                else:
                    error_msg = result.stderr.strip()
                    # Don't treat "NoSuchKey" or "does not exist" as errors
                    if any(phrase in error_msg for phrase in ["NoSuchKey", "does not exist", "NoSuchBucket"]):
                        print(f"[i] No files found in {directory}")
                    else:
                        print(f"[!] Warning: Failed to remove {directory}: {error_msg}")
                        cleanup_success = False
                        
            except subprocess.TimeoutExpired:
                print(f"[!] Warning: Timeout while removing {directory}")
                cleanup_success = False
            except Exception as e:
                print(f"[!] Warning: Error removing {directory}: {e}")
                cleanup_success = False
        
        # Step 2: Clean up files matching temporary patterns
        print(f"[+] Cleaning up files matching {len(self.TEMP_FILE_PATTERNS)} temporary patterns...")
        for pattern in self.TEMP_FILE_PATTERNS:
            try:
                print(f"[+] Removing files matching pattern {pattern}...")
                cmd = ["aws", "s3", "rm", f"s3://{self.bucket_name}/", "--recursive", 
                       "--exclude", "*", "--include", pattern]
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=self.timeout, env=self.env)
                if result.returncode == 0:
                    deleted_count = result.stdout.count("delete:")
                    if deleted_count > 0:
                        print(f"[✓] Removed {deleted_count} files matching pattern {pattern}")
                        total_deleted += deleted_count
                    else:
                        print(f"[i] No files found matching pattern {pattern}")
                else:
                    error_msg = result.stderr.strip()
                    if not any(phrase in error_msg for phrase in ["NoSuchKey", "does not exist", "NoSuchBucket"]):
                        print(f"[!] Warning: Failed to clean pattern {pattern}: {error_msg}")
                        cleanup_success = False
            except subprocess.TimeoutExpired:
                print(f"[!] Warning: Timeout while cleaning pattern {pattern}")
                cleanup_success = False
            except Exception as e:
                print(f"[!] Warning: Error cleaning pattern {pattern}: {e}")
                cleanup_success = False
        
        # Step 3: Final summary
        print(f"\n{'='*60}")
        if cleanup_success:
            print(f"[✓] GLOBAL AWS S3 CLEANUP COMPLETED SUCCESSFULLY")
        else:
            print(f"[!] GLOBAL AWS S3 CLEANUP COMPLETED WITH WARNINGS")
        
        if total_deleted > 0:
            print(f"[i] Total files removed: {total_deleted}")
        else:
            print(f"[i] No temporary files found to remove")
        print(f"{'='*60}")
        
        return cleanup_success, total_deleted
    
    def cleanup_directories(self, 
                          directories: Optional[List[str]] = None,
                          workflow_type: str = "general") -> Tuple[bool, int]:
        """
        Clean up specified directories in the S3 bucket.
        This method is kept for backward compatibility but redirects to global_cleanup.
        
        Args:
            directories: List of directory paths to clean (ignored, uses global cleanup)
            workflow_type: Type of workflow for logging purposes (ignored)
            
        Returns:
            Tuple[bool, int]: (success_status, total_files_deleted)
        """
        print(f"[i] Redirecting to global cleanup (directories parameter ignored)")
        return self.global_cleanup()


# Main convenience function - this should be used by all workflows
def cleanup_aws_s3_temp_files(bucket_name: str = "lithops-us-east-1-45dk") -> bool:
    """
    Global cleanup function for all AWS S3 temporary files.
    This function should be used by all workflows instead of specific cleanup functions.
    
    Args:
        bucket_name: The S3 bucket name to clean
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    cleaner = S3Cleaner(bucket_name)
    success, _ = cleaner.global_cleanup()
    return success


# Legacy functions for backward compatibility - all redirect to global cleanup
def cleanup_ml_temp_files(bucket_name: str = "lithops-us-east-1-45dk") -> bool:
    """
    Legacy function - redirects to global cleanup.
    
    Args:
        bucket_name: The S3 bucket name to clean
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    print("[i] cleanup_ml_temp_files is deprecated. Using global cleanup instead.")
    return cleanup_aws_s3_temp_files(bucket_name)


def cleanup_video_temp_files(bucket_name: str = "lithops-us-east-1-45dk") -> bool:
    """
    Legacy function - redirects to global cleanup.
    
    Args:
        bucket_name: The S3 bucket name to clean
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    print("[i] cleanup_video_temp_files is deprecated. Using global cleanup instead.")
    return cleanup_aws_s3_temp_files(bucket_name)


def cleanup_all_workflows(bucket_name: str = "lithops-us-east-1-45dk") -> bool:
    """
    Legacy function - redirects to global cleanup.
    
    Args:
        bucket_name: The S3 bucket name to clean
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    print("[i] cleanup_all_workflows is deprecated. Using global cleanup instead.")
    return cleanup_aws_s3_temp_files(bucket_name)


# Main execution for testing
if __name__ == "__main__":
    print("Testing AWS S3 Global Cleanup...")
    success = cleanup_aws_s3_temp_files()
    if success:
        print("Cleanup completed successfully!")
    else:
        print("Cleanup completed with warnings.")

"""
Upload dataset to S3 bucket.

Example usage:
    python scripts/upload_to_s3.py --input data/questions --bucket your-bucket --prefix datasets/
"""

import argparse
from pathlib import Path
import boto3
from botocore.exceptions import ClientError


def upload_directory_to_s3(local_dir: Path, bucket_name: str, s3_prefix: str = ""):
    """Upload entire directory to S3, preserving structure.
    
    Args:
        local_dir: Local directory to upload
        bucket_name: S3 bucket name
        s3_prefix: Prefix for S3 keys (e.g., 'datasets/')
    """
    
    s3_client = boto3.client('s3')
    
    # Get all files in directory
    files = list(local_dir.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    print(f"Found {len(files)} files to upload...")
    
    uploaded = 0
    failed = 0
    
    for file_path in files:
        # Calculate relative path and S3 key
        relative_path = file_path.relative_to(local_dir)
        s3_key = f"{s3_prefix}{relative_path}".replace("\\", "/")
        
        # Upload file
        if upload_file_to_s3(file_path, bucket_name, s3_key, s3_client):
            uploaded += 1
            if uploaded % 10 == 0:
                print(f"Uploaded {uploaded}/{len(files)} files...")
        else:
            failed += 1
            print(f"Failed to upload: {file_path}")
    
    print(f"\n✓ Upload complete: {uploaded} successful, {failed} failed")
    return uploaded, failed


def upload_file_to_s3(file_path: Path, bucket_name: str, s3_key: str, s3_client) -> bool:
    """Upload a single file to S3."""
    
    # Determine content type based on file extension
    content_type = get_content_type(file_path)
    
    extra_args = {"ContentType": content_type} if content_type else {}
    
    s3_client.upload_file(
        str(file_path),
        bucket_name,
        s3_key,
        ExtraArgs=extra_args
    )
    return True


def get_content_type(file_path: Path) -> str:
    """Get content type based on file extension."""
    extension = file_path.suffix.lower()
    
    content_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".json": "application/json",
        ".txt": "text/plain",
        ".mp4": "video/mp4",
    }
    
    return content_types.get(extension, "application/octet-stream")


def download_from_s3(bucket_name: str, s3_prefix: str, local_dir: Path):
    """Download dataset from S3 to local directory.
    
    Args:
        bucket_name: S3 bucket name
        s3_prefix: S3 prefix to download from
        local_dir: Local directory to save files
    """
    
    s3_client = boto3.client('s3')
    
    print(f"Downloading from s3://{bucket_name}/{s3_prefix}...")
    
    # List all objects with prefix
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)
    
    files = []
    for page in pages:
        if 'Contents' in page:
            files.extend(page['Contents'])
    
    print(f"Found {len(files)} files to download...")
    
    downloaded = 0
    for obj in files:
        s3_key = obj['Key']
        
        # Calculate local path
        relative_path = s3_key.replace(s3_prefix, "", 1).lstrip("/")
        local_path = local_dir / relative_path
        
        # Create directory
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        s3_client.download_file(bucket_name, s3_key, str(local_path))
        downloaded += 1
        
        if downloaded % 10 == 0:
            print(f"Downloaded {downloaded}/{len(files)} files...")
    
    print(f"\n✓ Download complete: {downloaded} files")
    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Upload/download datasets to/from S3")
    parser.add_argument("--action", type=str, choices=["upload", "download"], required=True, help="Action to perform")
    parser.add_argument("--input", type=Path, help="Input directory (for upload)")
    parser.add_argument("--output", type=Path, help="Output directory (for download)")
    parser.add_argument("--bucket", type=str, required=True, help="S3 bucket name")
    parser.add_argument("--prefix", type=str, default="", help="S3 prefix/path")
    
    args = parser.parse_args()
    
    if args.action == "upload":
        if not args.input:
            print("Error: --input required for upload")
            return
        if not args.input.exists():
            print(f"Error: Input directory does not exist: {args.input}")
            return
        
        upload_directory_to_s3(args.input, args.bucket, args.prefix)
    
    elif args.action == "download":
        if not args.output:
            print("Error: --output required for download")
            return
        
        args.output.mkdir(parents=True, exist_ok=True)
        download_from_s3(args.bucket, args.prefix, args.output)


if __name__ == "__main__":
    main()


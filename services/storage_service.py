"""
Media Upload Service
Supports local storage, AWS S3, and Cloudflare R2
"""

import os
import secrets
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx", "zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size_mb(file):
    """Get file size in MB"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size / (1024 * 1024)


class LocalStorageService:
    """Local filesystem storage"""
    
    def __init__(self, base_path="static/uploads"):
        self.base_path = base_path
        
    def upload(self, file, folder="general"):
        """Upload file to local storage"""
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        if get_file_size_mb(file) > 50:
            raise ValueError("File too large (max 50MB)")
        
        # Create folder
        upload_folder = os.path.join(self.base_path, folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{secrets.token_hex(8)}{ext}"
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        logger.info(f"Uploaded file: {filename}")
        return {
            "filename": filename,
            "filepath": filepath,
            "url": f"/{upload_folder}/{filename}",
            "size_mb": get_file_size_mb(file)
        }
    
    def delete(self, file_path):
        """Delete file from local storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


class S3StorageService:
    """AWS S3 storage (requires boto3)"""
    
    def __init__(self, bucket_name, region="us-east-1", access_key=None, secret_key=None):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            self.bucket_name = bucket_name
        except ImportError:
            raise ImportError("boto3 not installed. Install with: pip install boto3")
    
    def upload(self, file, folder="general"):
        """Upload file to S3"""
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        if get_file_size_mb(file) > 50:
            raise ValueError("File too large (max 50MB)")
        
        # Generate unique key
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        key = f"{folder}/{base}_{secrets.token_hex(8)}{ext}"
        
        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            logger.info(f"Uploaded to S3: {key}")
            
            return {
                "filename": filename,
                "key": key,
                "url": url,
                "size_mb": get_file_size_mb(file)
            }
        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            raise
    
    def delete(self, key):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted from S3: {key}")
            return True
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False


class CloudflareR2StorageService:
    """Cloudflare R2 storage (S3-compatible)"""
    
    def __init__(self, bucket_name, account_id, access_key, secret_key):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name="auto"
            )
            self.bucket_name = bucket_name
            self.cdn_url = f"https://cdn.example.com"  # Configure your R2 public URL
        except ImportError:
            raise ImportError("boto3 not installed. Install with: pip install boto3")
    
    def upload(self, file, folder="general"):
        """Upload file to Cloudflare R2"""
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        if get_file_size_mb(file) > 50:
            raise ValueError("File too large (max 50MB)")
        
        # Generate unique key
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        key = f"{folder}/{base}_{secrets.token_hex(8)}{ext}"
        
        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            url = f"{self.cdn_url}/{key}"
            logger.info(f"Uploaded to R2: {key}")
            
            return {
                "filename": filename,
                "key": key,
                "url": url,
                "size_mb": get_file_size_mb(file)
            }
        except Exception as e:
            logger.error(f"R2 upload error: {e}")
            raise
    
    def delete(self, key):
        """Delete file from R2"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted from R2: {key}")
            return True
        except Exception as e:
            logger.error(f"R2 delete error: {e}")
            return False


def get_storage_service(storage_type="local", **kwargs):
    """Factory function to get storage service instance"""
    if storage_type == "local":
        return LocalStorageService(kwargs.get("base_path", "static/uploads"))
    elif storage_type == "s3":
        return S3StorageService(
            bucket_name=kwargs.get("bucket_name"),
            region=kwargs.get("region", "us-east-1"),
            access_key=kwargs.get("access_key"),
            secret_key=kwargs.get("secret_key")
        )
    elif storage_type == "r2":
        return CloudflareR2StorageService(
            bucket_name=kwargs.get("bucket_name"),
            account_id=kwargs.get("account_id"),
            access_key=kwargs.get("access_key"),
            secret_key=kwargs.get("secret_key")
        )
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

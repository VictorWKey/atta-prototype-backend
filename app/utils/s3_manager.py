import boto3
from botocore.exceptions import ClientError
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.aws_s3_bucket
        
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
    
    def upload_file(self, file_path: str, object_name: str) -> bool:
        """Upload a file to S3 bucket."""
        if not self.s3_client:
            logger.warning("S3 client not configured")
            return False
        
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False
    
    def upload_fileobj(self, file_obj, object_name: str) -> bool:
        """Upload a file object to S3 bucket."""
        if not self.s3_client:
            logger.warning("S3 client not configured")
            return False
        
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, object_name)
            return True
        except ClientError as e:
            logger.error(f"Error uploading file object to S3: {e}")
            return False
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for an S3 object."""
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """Delete a file from S3 bucket."""
        if not self.s3_client:
            logger.warning("S3 client not configured")
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False

# Global S3 manager instance
s3_manager = S3Manager()

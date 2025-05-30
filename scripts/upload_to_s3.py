# This script uploads a local data file to an S3 bucket.
# In production, you would typically extract data directly from the source,
# and not upload local files like this. This is mainly for testing or initial load.

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError

# Load environment variables from .env
load_dotenv()

# Environment variables (should be set in .env file)
BUCKET_NAME = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY") # S3 object key (i.e., path/filename in S3)
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")

def upload_to_s3():
    """Uploads a local file to the specified S3 bucket."""
    try:
        s3 = boto3.client('s3')
        s3.upload_file(LOCAL_FILE_PATH, BUCKET_NAME, S3_KEY)
        print(f"✅ Uploaded {LOCAL_FILE_PATH} to s3://{BUCKET_NAME}/{S3_KEY}")
    except FileNotFoundError:
        print(f"❌ File not found: {LOCAL_FILE_PATH}")
    except NoCredentialsError:
        print("❌ AWS credentials not found. Configure them via AWS CLI or environment variables.")
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")

if __name__ == '__main__':
    upload_to_s3()

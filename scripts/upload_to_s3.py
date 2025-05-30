import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError

# Load environment variables from .env
load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")

def upload_to_s3():
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

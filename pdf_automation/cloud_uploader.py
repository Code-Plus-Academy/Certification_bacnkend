import os
import uuid
import json
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def upload_to_supabase(file_path, bucket_name=None, destination_path=None):
    """
    Uploads a file to Supabase Storage using environment variables or HTTP API.
    Env Vars Required: SUPABASE_URL, SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY), optional SUPABASE_BUCKET
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    bucket_name = bucket_name or os.environ.get("SUPABASE_BUCKET", "certificates")
    
    if not supabase_url or not supabase_key:
        return None
        
    filename = os.path.basename(file_path)
    if not destination_path:
        destination_path = f"certificates/{datetime.now().strftime('%Y/%m')}/{filename}"
        
    try:
        import requests
        upload_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket_name}/{destination_path}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": "application/pdf"
        }
        with open(file_path, 'rb') as f:
            response = requests.post(upload_endpoint, headers=headers, data=f)
            
        if response.status_code in [200, 201]:
            public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/{destination_path}"
            return public_url
        else:
            print(f"[STORAGE WARNING] Supabase upload error: {response.text}")
            return None
    except Exception as e:
        print(f"[STORAGE WARNING] Supabase exception: {e}")
        return None

def upload_to_s3(file_path, bucket_name=None, destination_path=None):
    """
    Uploads a file to AWS S3 bucket.
    Env Vars Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME
    """
    bucket_name = bucket_name or os.environ.get("S3_BUCKET_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    if not bucket_name or not os.environ.get("AWS_ACCESS_KEY_ID"):
        return None
        
    filename = os.path.basename(file_path)
    if not destination_path:
        destination_path = f"certificates/{filename}"
        
    try:
        import boto3
        s3_client = boto3.client('s3', region_name=region)
        s3_client.upload_file(file_path, bucket_name, destination_path, ExtraArgs={'ContentType': 'application/pdf'})
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{destination_path}"
        return s3_url
    except Exception as e:
        print(f"[STORAGE WARNING] S3 upload exception: {e}")
        return None

def upload_to_cloudinary(file_path, folder="certificates"):
    """
    Uploads a file to Cloudinary.
    Env Vars Required: CLOUDINARY_URL or (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
    """
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    
    if not os.environ.get("CLOUDINARY_URL") and not (cloud_name and api_key and api_secret):
        return None
        
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        upload_result = cloudinary.uploader.upload(
            file_path, 
            resource_type="raw", 
            folder=folder
        )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"[STORAGE WARNING] Cloudinary upload exception: {e}")
        return None

def process_cloud_uploads(file_path, req_base_url="http://localhost:5000"):
    """
    Uploads generated PDF to enabled cloud providers and returns structured URLs map.
    """
    filename = os.path.basename(file_path)
    local_url = f"{req_base_url.rstrip('/')}/output/{filename}"
    
    urls = {
        "local_download_url": local_url,
        "supabase_url": upload_to_supabase(file_path),
        "s3_url": upload_to_s3(file_path),
        "cloudinary_url": upload_to_cloudinary(file_path)
    }
    
    # Filter out None values
    active_cloud_urls = {k: v for k, v in urls.items() if v is not None}
    return active_cloud_urls

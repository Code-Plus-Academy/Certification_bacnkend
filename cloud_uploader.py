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
    supabase_key = (
        os.environ.get("SUPABASE_SECRET_KEY") or 
        os.environ.get("SUPABASE_KEY") or 
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or 
        os.environ.get("SUPABASE_SERVICE_KEY") or
        os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    )
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

def _get_supabase_config():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = (
        os.environ.get("SUPABASE_SECRET_KEY") or 
        os.environ.get("SUPABASE_KEY") or 
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or 
        os.environ.get("SUPABASE_SERVICE_KEY") or
        os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    )
    bucket_name = os.environ.get("SUPABASE_BUCKET", "certificates")
    return supabase_url, supabase_key, bucket_name

def upload_template_to_supabase(template_filename, html_content):
    """
    Uploads custom HTML template to Supabase Storage under templates/{template_filename}.
    Overwrites existing template if already present.
    """
    supabase_url, supabase_key, bucket_name = _get_supabase_config()
    if not supabase_url or not supabase_key:
        return None

    if not template_filename.endswith('.html'):
        template_filename += '.html'

    destination_path = f"templates/{template_filename}"
    try:
        import requests
        upload_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket_name}/{destination_path}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": "text/html; charset=utf-8",
            "x-upsert": "true"
        }
        encoded_content = html_content.encode('utf-8')
        response = requests.post(upload_endpoint, headers=headers, data=encoded_content)

        if response.status_code in [200, 201]:
            public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/{destination_path}"
            print(f"[OK] Template '{template_filename}' backed up to Supabase Storage: {public_url}")
            return public_url
        else:
            print(f"[STORAGE WARNING] Supabase template upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"[STORAGE WARNING] Exception uploading template to Supabase: {e}")
        return None

def fetch_templates_from_supabase(target_dir):
    """
    Lists objects in templates/ folder in Supabase Storage and downloads them to target_dir.
    Returns list of downloaded filenames.
    """
    supabase_url, supabase_key, bucket_name = _get_supabase_config()
    if not supabase_url or not supabase_key or not target_dir:
        return []

    os.makedirs(target_dir, exist_ok=True)
    downloaded = []
    try:
        import requests
        list_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/list/{bucket_name}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": "application/json"
        }
        payload = {"prefix": "templates/", "limit": 100}
        resp = requests.post(list_endpoint, headers=headers, json=payload)
        if resp.status_code == 200:
            files = resp.json()
            for obj in files:
                fname = obj.get('name')
                if fname and fname.endswith('.html'):
                    file_path = os.path.join(target_dir, fname)
                    download_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/templates/{fname}"
                    down_resp = requests.get(download_url, headers=headers)
                    if down_resp.status_code == 200:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(down_resp.text)
                        downloaded.append(fname)
                        print(f"[OK] Synced template '{fname}' from Supabase to local storage.")
        else:
            print(f"[STORAGE WARNING] Supabase list templates failed ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"[STORAGE WARNING] Exception syncing templates from Supabase: {e}")

    return downloaded

def download_single_template_from_supabase(template_filename, target_dir):
    """
    Downloads a single missing template from Supabase Storage templates/{template_filename} if available.
    """
    supabase_url, supabase_key, bucket_name = _get_supabase_config()
    if not supabase_url or not supabase_key or not target_dir:
        return None

    if not template_filename.endswith('.html'):
        template_filename += '.html'

    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, template_filename)
    try:
        import requests
        download_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/templates/{template_filename}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key
        }
        resp = requests.get(download_url, headers=headers)
        if resp.status_code == 200 and resp.text.strip():
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f"[OK] On-demand download of template '{template_filename}' from Supabase succeeded.")
            return target_path
    except Exception as e:
        print(f"[STORAGE WARNING] Exception downloading template '{template_filename}' from Supabase: {e}")
    return None

def delete_template_from_supabase(template_filename):
    """
    Deletes template from templates/{template_filename} in Supabase Storage.
    """
    supabase_url, supabase_key, bucket_name = _get_supabase_config()
    if not supabase_url or not supabase_key:
        return False

    if not template_filename.endswith('.html'):
        template_filename += '.html'

    destination_path = f"templates/{template_filename}"
    try:
        import requests
        delete_endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket_name}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": "application/json"
        }
        payload = {"prefixes": [destination_path]}
        resp = requests.delete(delete_endpoint, headers=headers, json=payload)
        if resp.status_code in [200, 204]:
            print(f"[OK] Template '{template_filename}' removed from Supabase Storage.")
            return True
        else:
            print(f"[STORAGE WARNING] Supabase template deletion failed: {resp.text}")
            return False
    except Exception as e:
        print(f"[STORAGE WARNING] Exception deleting template '{template_filename}' from Supabase: {e}")
        return False

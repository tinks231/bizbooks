"""
Vercel Blob Storage utilities
For uploading files to Vercel Blob Storage (free tier: 1GB)
"""
import os
import requests
from datetime import datetime

def upload_to_vercel_blob(file_data, filename, content_type='image/jpeg'):
    """
    Upload file to Vercel Blob Storage
    
    Args:
        file_data: File bytes or file-like object
        filename: Name for the file (e.g., 'employee123_20250125.jpg')
        content_type: MIME type (default: 'image/jpeg')
    
    Returns:
        str: Public URL of uploaded file, or None if upload fails
    """
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    
    if not blob_token:
        print("⚠️  BLOB_READ_WRITE_TOKEN not found. Cannot upload to Vercel Blob.")
        return None
    
    try:
        # Read file data if it's a file-like object
        if hasattr(file_data, 'read'):
            file_bytes = file_data.read()
            # Reset file pointer if needed
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
        else:
            file_bytes = file_data
        
        # Vercel Blob API endpoint
        url = f"https://blob.vercel-storage.com/{filename}"
        
        headers = {
            'Authorization': f'Bearer {blob_token}',
            'X-Content-Type': content_type,
            'X-Add-Random-Suffix': '1',  # Prevent filename collisions
        }
        
        # Upload file
        response = requests.put(url, data=file_bytes, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            public_url = result.get('url')
            print(f"✅ Uploaded to Vercel Blob: {public_url}")
            return public_url
        else:
            print(f"❌ Vercel Blob upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading to Vercel Blob: {e}")
        return None


def delete_from_vercel_blob(file_url):
    """
    Delete file from Vercel Blob Storage
    
    Args:
        file_url: Full URL of the file to delete
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
    
    if not blob_token:
        print("⚠️  BLOB_READ_WRITE_TOKEN not found. Cannot delete from Vercel Blob.")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {blob_token}',
        }
        
        # Delete request
        response = requests.delete(file_url, headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"✅ Deleted from Vercel Blob: {file_url}")
            return True
        else:
            print(f"⚠️ Vercel Blob delete failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting from Vercel Blob: {e}")
        return False


def generate_blob_filename(prefix, employee_name=None, extension='jpg'):
    """
    Generate a unique filename for Vercel Blob Storage
    
    Args:
        prefix: 'attendance' or 'document'
        employee_name: Optional employee name for better organization
        extension: File extension (default: 'jpg')
    
    Returns:
        str: Filename like 'attendance/john_doe_20250125_143055.jpg'
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if employee_name:
        # Sanitize employee name (remove spaces, special chars)
        safe_name = "".join(c if c.isalnum() else "_" for c in employee_name.lower())
        return f"{prefix}/{safe_name}_{timestamp}.{extension}"
    
    return f"{prefix}/{timestamp}.{extension}"

